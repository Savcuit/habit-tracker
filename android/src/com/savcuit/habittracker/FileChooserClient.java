package com.savcuit.habittracker;

import android.net.Uri;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;

/** Hands the page's file picker request to the activity. */
public class FileChooserClient extends WebChromeClient {

    public interface Host {
        void openFilePicker(ValueCallback<Uri[]> callback);
    }

    private final Host host;

    FileChooserClient(Host host) {
        this.host = host;
    }

    @Override
    public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback,
                                     FileChooserParams params) {
        host.openFilePicker(callback);
        return true;
    }
}
