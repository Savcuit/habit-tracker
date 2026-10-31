package com.savcuit.habittracker;

import android.app.Activity;
import android.content.ContentValues;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.webkit.JavascriptInterface;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

/**
 * WebView cannot download files on its own, so backups are written through this bridge
 * into the public Downloads folder (Android 10+) or the app's external files folder.
 */
public class Backup {

    private final Activity activity;

    Backup(Activity activity) {
        this.activity = activity;
    }

    @JavascriptInterface
    public String save(String json, String filename) {
        if (json == null || json.length() == 0) return "error: nothing to save";
        if (filename == null || filename.length() == 0) filename = "habits-backup.json";

        try {
            byte[] bytes = json.getBytes("UTF-8");

            if (Build.VERSION.SDK_INT >= 29) {
                ContentValues values = new ContentValues();
                values.put(MediaStore.Downloads.DISPLAY_NAME, filename);
                values.put(MediaStore.Downloads.MIME_TYPE, "application/json");
                values.put(MediaStore.Downloads.IS_PENDING, 1);

                Uri uri = activity.getContentResolver()
                        .insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values);
                if (uri == null) return "error: could not create the file";

                OutputStream out = activity.getContentResolver().openOutputStream(uri);
                out.write(bytes);
                out.close();

                values.clear();
                values.put(MediaStore.Downloads.IS_PENDING, 0);
                activity.getContentResolver().update(uri, values, null, null);
                return "Downloads/" + filename;
            }

            File dir = activity.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS);
            if (dir == null) dir = activity.getFilesDir();
            File file = new File(dir, filename);
            FileOutputStream out = new FileOutputStream(file);
            out.write(bytes);
            out.close();
            return file.getAbsolutePath();
        } catch (Exception e) {
            return "error: " + e.getMessage();
        }
    }
}
