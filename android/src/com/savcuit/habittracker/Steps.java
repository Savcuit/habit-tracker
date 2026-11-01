package com.savcuit.habittracker;

import android.app.Activity;
import android.content.Context;
import android.content.SharedPreferences;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Build;
import android.webkit.JavascriptInterface;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

/**
 * Reads the phone's step counter so a habit like "10,000 steps" can be checked by the device
 * rather than trusted to the user.
 *
 * The sensor reports steps since the last reboot, so the app keeps a baseline taken at the start
 * of each day; today's figure is current minus that baseline.
 */
public class Steps {

    private static final String PREFS = "steps";
    private static final String KEY_DATE = "date";
    private static final String KEY_BASE = "baseline";
    private static final String KEY_LAST_RAW = "lastRaw";
    private static final String KEY_LAST_AT = "lastRawAt";

    private final Activity activity;

    Steps(Activity activity) {
        this.activity = activity;
    }

    private SensorManager sensors() {
        return (SensorManager) activity.getSystemService(Context.SENSOR_SERVICE);
    }

    private Sensor stepSensor() {
        SensorManager sm = sensors();
        if (sm == null) return null;
        Sensor sensor = sm.getDefaultSensor(Sensor.TYPE_STEP_COUNTER);
        if (sensor == null) sensor = sm.getDefaultSensor(Sensor.TYPE_STEP_DETECTOR);
        return sensor;
    }

    @JavascriptInterface
    public boolean available() {
        return stepSensor() != null;
    }

    @JavascriptInterface
    public boolean permissionNeeded() {
        if (Build.VERSION.SDK_INT < 29) return false;
        return activity.checkSelfPermission("android.permission.ACTIVITY_RECOGNITION")
                != android.content.pm.PackageManager.PERMISSION_GRANTED;
    }

    /** Steps recorded today, or -1 when the phone has no step sensor. */
    @JavascriptInterface
    public int todaySteps() {
        Sensor sensor = stepSensor();
        if (sensor == null) return -1;

        float raw = readOnce(sensor);
        if (Float.isNaN(raw)) return -1;

        long current = (long) raw;
        SharedPreferences prefs = activity.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        String today = today();
        String storedDate = prefs.getString(KEY_DATE, "");
        long baseline = prefs.getLong(KEY_BASE, -1);

        if (!today.equals(storedDate) || baseline < 0) {
            // No reading yet today. If the phone was seen recently and has not rebooted,
            // the last reading is a far better starting point than the current one.
            long previous = prefs.getLong(KEY_LAST_RAW, -1);
            long previousAt = prefs.getLong(KEY_LAST_AT, 0);
            long hoursSince = (System.currentTimeMillis() - previousAt) / 3600000L;

            long start = current;
            if (previous > 0 && previous <= current && hoursSince < 20) start = previous;

            prefs.edit()
                 .putString(KEY_DATE, today)
                 .putLong(KEY_BASE, start)
                 .putLong(KEY_LAST_RAW, current)
                 .putLong(KEY_LAST_AT, System.currentTimeMillis())
                 .apply();
            return (int) Math.max(0, current - start);
        }

        prefs.edit()
             .putLong(KEY_LAST_RAW, current)
             .putLong(KEY_LAST_AT, System.currentTimeMillis())
             .apply();

        if (current < baseline) {
            // The phone rebooted and the counter restarted.
            prefs.edit().putLong(KEY_BASE, 0).apply();
            return (int) current;
        }

        return (int) Math.max(0, current - baseline);
    }

    /** Takes a fresh baseline; called just after midnight so the day starts at zero. */
    @JavascriptInterface
    public boolean resetBaseline() {
        Sensor sensor = stepSensor();
        if (sensor == null) return false;
        float raw = readOnce(sensor);
        if (Float.isNaN(raw)) return false;

        activity.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                .putString(KEY_DATE, today())
                .putLong(KEY_BASE, (long) raw)
                .apply();
        return true;
    }

    private float readOnce(Sensor sensor) {
        SensorManager sm = sensors();
        if (sm == null) return Float.NaN;

        StepListener listener = new StepListener();
        sm.registerListener(listener, sensor, SensorManager.SENSOR_DELAY_FASTEST);
        try {
            listener.latch.await(1500, TimeUnit.MILLISECONDS);
        } catch (InterruptedException ignored) { }
        sm.unregisterListener(listener);

        return listener.value;
    }

    /** A named listener keeps the dex compiler happy (it rejects anonymous ones here). */
    static class StepListener implements SensorEventListener {
        final CountDownLatch latch = new CountDownLatch(1);
        volatile float value = Float.NaN;

        @Override
        public void onSensorChanged(SensorEvent event) {
            if (event.values.length > 0) {
                value = event.values[0];
                latch.countDown();
            }
        }

        @Override
        public void onAccuracyChanged(Sensor sensor, int accuracy) { }
    }

    private static String today() {
        return new SimpleDateFormat("yyyy-MM-dd", Locale.US).format(new Date());
    }

    /** Used by the midnight alarm. */
    static void reset(Context context) {
        SensorManager sm = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
        if (sm == null) return;
        Sensor sensor = sm.getDefaultSensor(Sensor.TYPE_STEP_COUNTER);
        if (sensor == null) return;

        StepListener listener = new StepListener();
        sm.registerListener(listener, sensor, SensorManager.SENSOR_DELAY_FASTEST);
        try {
            listener.latch.await(1500, TimeUnit.MILLISECONDS);
        } catch (InterruptedException ignored) { }
        sm.unregisterListener(listener);

        if (Float.isNaN(listener.value)) return;

        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                .putString(KEY_DATE, new SimpleDateFormat("yyyy-MM-dd", Locale.US).format(new Date()))
                .putLong(KEY_BASE, (long) listener.value)
                .apply();
    }
}
