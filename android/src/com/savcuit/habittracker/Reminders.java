package com.savcuit.habittracker;

import android.app.Activity;
import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.webkit.JavascriptInterface;

import java.util.Calendar;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Bridge between the web page and Android's alarm system.
 * The page calls AndroidReminders.schedule(...) for every habit that has a time set.
 */
public class Reminders {

    static final String PREFS = "reminders";

    private final Activity activity;
    private final SharedPreferences prefs;

    Reminders(Activity activity) {
        this.activity = activity;
        this.prefs = activity.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
    }

    @JavascriptInterface
    public boolean supported() {
        return true;
    }

    @JavascriptInterface
    public void schedule(String id, int hour, int minute, String title, String body) {
        if (id == null || id.length() == 0) return;
        prefs.edit()
             .putString(id, hour + "|" + minute + "|" + clean(title) + "|" + clean(body))
             .apply();
        setAlarm(activity, id, hour, minute);
    }

    @JavascriptInterface
    public void cancel(String id) {
        if (id == null) return;
        prefs.edit().remove(id).apply();
        AlarmManager am = (AlarmManager) activity.getSystemService(Context.ALARM_SERVICE);
        if (am != null) am.cancel(pending(activity, id));
    }

    @JavascriptInterface
    public void cancelAll() {
        AlarmManager am = (AlarmManager) activity.getSystemService(Context.ALARM_SERVICE);
        if (am != null) {
            for (String key : prefs.getAll().keySet()) am.cancel(pending(activity, key));
        }
        prefs.edit().clear().apply();
    }

    @JavascriptInterface
    public int count() {
        return prefs.getAll().size();
    }

    /** Hands over habits the user completed from the notification, then clears the queue. */
    @JavascriptInterface
    public String takePending() {
        SharedPreferences pending = activity.getSharedPreferences(ActionReceiver.PENDING, Context.MODE_PRIVATE);
        Set<String> ids = pending.getStringSet("ids", new HashSet<String>());
        if (ids == null || ids.isEmpty()) return "[]";

        StringBuilder out = new StringBuilder("[");
        boolean first = true;
        for (String id : ids) {
            if (!first) out.append(",");
            out.append("\"").append(id.replace("\"", "")).append("\"");
            first = false;
        }
        out.append("]");

        pending.edit().putStringSet("ids", new HashSet<String>()).apply();
        return out.toString();
    }

    /** Schedules a single alarm one minute from now, so the user can see one arrive. */
    @JavascriptInterface
    public void test(String title, String body) {
        Calendar c = Calendar.getInstance();
        c.add(Calendar.MINUTE, 1);
        prefs.edit().putString("__test", "-1|-1|" + clean(title) + "|" + clean(body)).apply();

        Intent intent = new Intent(activity, ReminderReceiver.class).putExtra("id", "__test");
        intent.putExtra("direct_title", clean(title));
        intent.putExtra("direct_body", clean(body));

        AlarmManager am = (AlarmManager) activity.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
        PendingIntent pi = PendingIntent.getBroadcast(activity, 9999, intent, flags);
        am.setExact(AlarmManager.RTC_WAKEUP, c.getTimeInMillis(), pi);
    }

    // ---------------------------------------------------------------- internals

    private static String clean(String text) {
        if (text == null) return "";
        return text.replace("|", " ").trim();
    }

    private static PendingIntent pending(Context ctx, String id) {
        Intent intent = new Intent(ctx, ReminderReceiver.class).putExtra("id", id);
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
        return PendingIntent.getBroadcast(ctx, id.hashCode(), intent, flags);
    }

    private static void setAlarm(Context ctx, String id, int hour, int minute) {
        AlarmManager am = (AlarmManager) ctx.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;

        Calendar c = Calendar.getInstance();
        c.set(Calendar.HOUR_OF_DAY, hour);
        c.set(Calendar.MINUTE, minute);
        c.set(Calendar.SECOND, 0);
        c.set(Calendar.MILLISECOND, 0);
        if (c.getTimeInMillis() <= System.currentTimeMillis()) {
            c.add(Calendar.DAY_OF_YEAR, 1);
        }

        PendingIntent pi = pending(ctx, id);
        am.cancel(pi);
        // Inexact on purpose: it needs no special alarm permission and survives Doze.
        am.setInexactRepeating(AlarmManager.RTC_WAKEUP, c.getTimeInMillis(),
                               AlarmManager.INTERVAL_DAY, pi);
    }

    /** Re-registers every stored alarm; used after a reboot. */
    static void restoreAll(Context ctx) {
        SharedPreferences prefs = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        for (Map.Entry<String, ?> entry : prefs.getAll().entrySet()) {
            String raw = String.valueOf(entry.getValue());
            String[] parts = raw.split("\\|", 4);
            if (parts.length < 2) continue;
            try {
                int hour = Integer.parseInt(parts[0]);
                int minute = Integer.parseInt(parts[1]);
                if (hour < 0) continue;
                setAlarm(ctx, entry.getKey(), hour, minute);
            } catch (NumberFormatException ignored) { }
        }
    }
}
