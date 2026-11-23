package com.savcuit.habittracker;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

import java.util.Calendar;
import java.util.Random;

/**
 * The surprise nudges: a handful of reminders a day, at times the app chooses,
 * so they cannot be tuned out the way a fixed 9 a.m. alarm can.
 *
 * Windows: first one between 09:00 and 10:30, then gaps of 90 to 170 minutes,
 * nothing after 21:30. The next one is armed by the receiver that fires it, so
 * randomization continues even when the app is never opened.
 */
public final class RandomReminders {

    static final String KEY_ON = "random_on";
    static final String KEY_LAST = "random_last";
    static final String KEY_NEXT = "random_next";
    static final String KEY_PENDING = "random_pending";

    private static final int REQUEST = 4242;
    private static final int DAY_START = 9;      // 09:00
    private static final int DAY_END = 21;       // 21:30
    private static final int END_MINUTE = 30;
    private static final long MIN_GAP = 90L * 60 * 1000;
    private static final long MAX_GAP = 170L * 60 * 1000;

    private RandomReminders() {}

    private static SharedPreferences prefs(Context c) {
        return c.getSharedPreferences(Reminders.PREFS, Context.MODE_PRIVATE);
    }

    static boolean enabled(Context c) {
        return prefs(c).getBoolean(KEY_ON, false);
    }

    static void setEnabled(Context c, boolean on) {
        prefs(c).edit().putBoolean(KEY_ON, on).apply();
        if (on) scheduleNext(c, true);
        else cancel(c);
    }

    static void cancel(Context c) {
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        if (am != null) am.cancel(intent(c));
    }

    static long nextAt(Context c) {
        return prefs(c).getLong(KEY_NEXT, 0L);
    }

    static void scheduleNext(Context c, boolean firstOfDay) {
        if (!enabled(c)) return;
        long when = pickTime(c, firstOfDay);
        prefs(c).edit().putLong(KEY_NEXT, when).apply();

        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;

        PendingIntent pi = intent(c);
        try {
            if (Build.VERSION.SDK_INT >= 23) {
                am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, when, pi);
            } else {
                am.set(AlarmManager.RTC_WAKEUP, when, pi);
            }
        } catch (Exception ignored) {
        }
    }

    private static long pickTime(Context c, boolean firstOfDay) {
        Random random = new Random();
        Calendar now = Calendar.getInstance();
        long nowMs = now.getTimeInMillis();

        if (firstOfDay) {
            Calendar start = Calendar.getInstance();
            start.set(Calendar.HOUR_OF_DAY, DAY_START);
            start.set(Calendar.MINUTE, random.nextInt(90));   // 09:00 – 10:29
            start.set(Calendar.SECOND, 0);
            start.set(Calendar.MILLISECOND, 0);
            if (start.getTimeInMillis() > nowMs + 5 * 60 * 1000) return start.getTimeInMillis();
        }

        long last = Math.max(prefs(c).getLong(KEY_LAST, 0L), nowMs);
        long gap = MIN_GAP + (long) (random.nextDouble() * (MAX_GAP - MIN_GAP));
        long when = last + gap;

        Calendar end = Calendar.getInstance();
        end.set(Calendar.HOUR_OF_DAY, DAY_END);
        end.set(Calendar.MINUTE, END_MINUTE);
        end.set(Calendar.SECOND, 0);
        end.set(Calendar.MILLISECOND, 0);

        if (when > end.getTimeInMillis()) {
            // the day is finished: start again tomorrow morning
            Calendar tomorrow = Calendar.getInstance();
            tomorrow.add(Calendar.DAY_OF_YEAR, 1);
            tomorrow.set(Calendar.HOUR_OF_DAY, DAY_START);
            tomorrow.set(Calendar.MINUTE, random.nextInt(90));
            tomorrow.set(Calendar.SECOND, 0);
            tomorrow.set(Calendar.MILLISECOND, 0);
            return tomorrow.getTimeInMillis();
        }
        return when;
    }

    static void markFired(Context c) {
        prefs(c).edit().putLong(KEY_LAST, System.currentTimeMillis()).apply();
    }

    static String pending(Context c) {
        return prefs(c).getString(KEY_PENDING, "");
    }

    private static PendingIntent intent(Context c) {
        Intent i = new Intent(c, RandomReminderReceiver.class);
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
        return PendingIntent.getBroadcast(c, REQUEST, i, flags);
    }
}
