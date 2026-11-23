package com.savcuit.habittracker;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import java.util.Random;

/**
 * The surprise nudge itself: says something in the spirit of Duolingo, then arms
 * the next one at a fresh random time, so the rhythm keeps moving by itself.
 */
public class RandomReminderReceiver extends BroadcastReceiver {

    private static final String CHANNEL = "nudges";

    private static final String[] TITLES = {
            "Still time to keep the streak",
            "Pip, with a small reminder",
            "One tap and today counts",
            "The streak is watching",
            "A quiet nudge"
    };

    private static final String[] BODIES = {
            "Two minutes now is worth more than a perfect plan later.",
            "Whatever is left today, do the smallest piece of it.",
            "You have kept it going this long — do not hand it back at midnight.",
            "Done beats started. Go on.",
            "A missed day costs a freeze. A done day costs nothing."
    };

    @Override
    public void onReceive(Context context, Intent intent) {
        NotificationManager nm = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) {
            RandomReminders.scheduleNext(context, false);
            return;
        }

        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL, "Surprise nudges", NotificationManager.IMPORTANCE_DEFAULT);
            channel.setDescription("Reminders at times the app chooses, to keep a streak going");
            nm.createNotificationChannel(channel);
        }

        Random random = new Random();
        String pending = RandomReminders.pending(context);
        String title = TITLES[random.nextInt(TITLES.length)];
        String body = pending != null && pending.length() > 0
                ? "Still open: " + pending + ". " + BODIES[random.nextInt(BODIES.length)]
                : BODIES[random.nextInt(BODIES.length)];

        Intent open = new Intent(context, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
        PendingIntent tap = PendingIntent.getActivity(context, 9001, open, flags);

        Notification.Builder builder = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(context, CHANNEL)
                : new Notification.Builder(context);

        builder.setContentTitle(title)
                .setContentText(body)
                .setStyle(new Notification.BigTextStyle().bigText(body))
                .setSmallIcon(android.R.drawable.ic_popup_reminder)
                .setAutoCancel(true)
                .setContentIntent(tap);

        nm.notify(9001, builder.build());

        RandomReminders.markFired(context);
        RandomReminders.scheduleNext(context, false);
    }
}
