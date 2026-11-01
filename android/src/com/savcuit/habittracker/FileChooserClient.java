package com.savcuit.habittracker;

import android.net.Uri;
import android.webkit.PermissionRequest;
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
    public void onPermissionRequest(PermissionRequest request) {
        // Called on the UI thread; the camera page only ever asks for video.
        try {
            for (String resource : request.getResources()) {
                if (!PermissionRequest.RESOURCE_VIDEO_CAPTURE.equals(resource)) {
                    request.deny();
                    return;
                }
            }
            request.grant(request.getResources());
        } catch (Exception e) {
            request.deny();
        }
    }

    @Override
    public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback,
                                     FileChooserParams params) {
        host.openFilePicker(callback);
        return true;
    }
}
