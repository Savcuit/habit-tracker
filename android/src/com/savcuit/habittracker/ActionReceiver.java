package com.savcuit.habittracker;

import android.app.AlarmManager;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

import java.util.HashSet;
import java.util.Set;

/**
 * Handles the two buttons on a reminder notification.
 * "Done" records the habit for today so the page can settle it when it next opens;
 * "Snooze" simply re-arms the same reminder a quarter of an hour later.
 */
public class ActionReceiver extends BroadcastReceiver {

    static final String PENDING = "pending_done";

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null) return;

        String action = intent.getStringExtra("action");
        String id = intent.getStringExtra("id");
        if (id == null) return;

        NotificationManager nm =
                (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm != null) nm.cancel(id.hashCode());

        if ("done".equals(action)) {
            SharedPreferences pending =
                    context.getSharedPreferences(PENDING, Context.MODE_PRIVATE);
            Set<String> marks = new HashSet<>(pending.getStringSet("ids", new HashSet<String>()));
            marks.add(id);
            pending.edit().putStringSet("ids", marks).apply();
        } else if ("snooze".equals(action)) {
            AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
            if (am == null) return;

            Intent again = new Intent(context, ReminderReceiver.class).putExtra("id", id);
            int flags = PendingIntent.FLAG_UPDATE_CURRENT;
            if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
            PendingIntent pi = PendingIntent.getBroadcast(context, id.hashCode() + 7, again, flags);

            long when = System.currentTimeMillis() + 15 * 60 * 1000L;
            am.set(AlarmManager.RTC_WAKEUP, when, pi);
        }
    }
}
