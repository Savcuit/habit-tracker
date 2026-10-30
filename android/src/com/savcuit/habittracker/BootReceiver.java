package com.savcuit.habittracker;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Android forgets repeating alarms across a reboot; put them back. */
public class BootReceiver extends BroadcastReceiver {

    @Override
    public void onReceive(Context context, Intent intent) {
        if (intent == null || intent.getAction() == null) return;
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            Reminders.restoreAll(context);
        }
    }
}
