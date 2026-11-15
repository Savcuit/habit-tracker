package com.savcuit.habittracker;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationManager;
import android.os.Build;
import android.webkit.JavascriptInterface;

/**
 * Gives the page one thing: roughly where the phone is, so the cosy colours can
 * follow the local weather. Coarse only, never tracked, never sent anywhere but
 * to the weather service.
 */
public class Geo {

    private static final int REQUEST = 71;
    private final Activity activity;

    public Geo(Activity activity) {
        this.activity = activity;
    }

    @JavascriptInterface
    public boolean permissionNeeded() {
        return activity.checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION)
                != PackageManager.PERMISSION_GRANTED;
    }

    @JavascriptInterface
    public void requestPermission() {
        activity.runOnUiThread(() -> activity.requestPermissions(
                new String[]{Manifest.permission.ACCESS_COARSE_LOCATION}, REQUEST));
    }

    @JavascriptInterface
    public String lastLocation() {
        try {
            if (permissionNeeded()) return "";
            LocationManager lm = (LocationManager) activity.getSystemService(Context.LOCATION_SERVICE);
            if (lm == null) return "";

            Location best = null;
            String[] providers = {LocationManager.NETWORK_PROVIDER, LocationManager.GPS_PROVIDER,
                    LocationManager.PASSIVE_PROVIDER};
            for (String provider : providers) {
                Location one = null;
                try {
                    one = lm.getLastKnownLocation(provider);
                } catch (Exception ignored) {
                }
                if (one != null && (best == null || one.getTime() > best.getTime())) best = one;
            }
            if (best == null) return "";
            return best.getLatitude() + "," + best.getLongitude();
        } catch (Exception e) {
            return "";
        }
    }
}
