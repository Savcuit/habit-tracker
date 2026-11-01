package com.savcuit.habittracker;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity implements FileChooserClient.Host {

    private static final int FILE_REQUEST = 43;

    private WebView web;
    private ValueCallback<Uri[]> fileCallback;

    @Override
    protected void onCreate(Bundle saved) {
        super.onCreate(saved);

        if (Build.VERSION.SDK_INT >= 21) {
            Window w = getWindow();
            w.setStatusBarColor(Color.parseColor("#0a1120"));
            w.setNavigationBarColor(Color.parseColor("#0a1120"));
        }

        askForNotificationPermission();

        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#0a1120"));

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setSupportZoom(false);
        s.setBuiltInZoomControls(false);
        s.setTextZoom(100);

        web.addJavascriptInterface(new Reminders(this), "AndroidReminders");
        web.addJavascriptInterface(new Backup(this), "AndroidBackup");
        web.addJavascriptInterface(new Steps(this), "AndroidSteps");

        // Without a chrome client the page's file picker never opens, so Import did nothing.
        web.setWebChromeClient(new FileChooserClient(this));

        web.setWebViewClient(new WebViewClient());
        web.setOverScrollMode(View.OVER_SCROLL_NEVER);
        setContentView(web);

        web.loadUrl(pageUrl(getIntent()));
    }

    private static String pageUrl(Intent intent) {
        String page = intent == null ? null : intent.getStringExtra("page");
        String base = "file:///android_asset/index.html";
        if (page == null || page.length() == 0) return base;
        return base + "#" + page;
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        if (web != null) web.loadUrl(pageUrl(intent));
    }

    @Override
    public void openFilePicker(android.webkit.ValueCallback<android.net.Uri[]> callback) {
        if (fileCallback != null) fileCallback.onReceiveValue(null);
        fileCallback = callback;

        Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
        intent.addCategory(Intent.CATEGORY_OPENABLE);
        intent.setType("*/*");
        startActivityForResult(Intent.createChooser(intent, "Select your backup"), FILE_REQUEST);
    }

    @Override
    protected void onActivityResult(int request, int result, Intent data) {
        if (request == FILE_REQUEST) {
            Uri[] chosen = null;
            if (result == RESULT_OK && data != null && data.getData() != null) {
                chosen = new Uri[]{data.getData()};
            }
            if (fileCallback != null) {
                fileCallback.onReceiveValue(chosen);
                fileCallback = null;
            }
            return;
        }
        super.onActivityResult(request, result, data);
    }

    private void askForNotificationPermission() {
        java.util.ArrayList<String> needed = new java.util.ArrayList<>();

        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
            needed.add(Manifest.permission.POST_NOTIFICATIONS);
        }
        if (Build.VERSION.SDK_INT >= 29
                && checkSelfPermission("android.permission.ACTIVITY_RECOGNITION")
                != PackageManager.PERMISSION_GRANTED) {
            needed.add("android.permission.ACTIVITY_RECOGNITION");
        }

        if (!needed.isEmpty()) {
            requestPermissions(needed.toArray(new String[0]), 1);
        }
    }

    @Override
    public void onBackPressed() {
        if (web != null && web.canGoBack()) {
            web.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
