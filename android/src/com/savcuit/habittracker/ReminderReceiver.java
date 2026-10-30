package com.savcuit.habittracker;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

/** Fires the reminder notification when an alarm goes off. */
public class ReminderReceiver extends BroadcastReceiver {

    private static final String CHANNEL = "habits";

    @Override
    public void onReceive(Context context, Intent intent) {
        String id = intent.getStringExtra("id");
        if (id == null) return;

        String title = intent.getStringExtra("direct_title");
        String body = intent.getStringExtra("direct_body");

        if (title == null) {
            SharedPreferences prefs = context.getSharedPreferences(Reminders.PREFS, Context.MODE_PRIVATE);
            String raw = prefs.getString(id, null);
            if (raw == null) return;
            String[] parts = raw.split("\\|", 4);
            title = parts.length > 2 && parts[2].length() > 0 ? parts[2] : "Habit Tracker";
            body = parts.length > 3 && parts[3].length() > 0 ? parts[3] : "Time for your habit";
        }

        NotificationManager nm =
                (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null) return;

        if (Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL, "Habit reminders", NotificationManager.IMPORTANCE_DEFAULT);
            channel.setDescription("Daily reminders for your habits");
            nm.createNotificationChannel(channel);
        }

        Intent open = new Intent(context, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
        PendingIntent tap = PendingIntent.getActivity(context, id.hashCode(), open, flags);

        Notification.Builder builder = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(context, CHANNEL)
                : new Notification.Builder(context);

        builder.setContentTitle(title)
               .setContentText(body)
               .setSmallIcon(android.R.drawable.ic_popup_reminder)
               .setAutoCancel(true)
               .setContentIntent(tap);

        nm.notify(id.hashCode(), builder.build());
    }
}
