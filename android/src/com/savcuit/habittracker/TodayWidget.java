package com.savcuit.habittracker;

import android.app.PendingIntent;
import android.appwidget.AppWidgetManager;
import android.appwidget.AppWidgetProvider;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.widget.RemoteViews;

/**
 * The home-screen widget: today's count, a bar, and whatever is still open.
 * The page writes one line of text into shared preferences; this reads it.
 */
public class TodayWidget extends AppWidgetProvider {

    public static void refresh(Context context) {
        try {
            AppWidgetManager manager = AppWidgetManager.getInstance(context);
            ComponentName name = new ComponentName(context, TodayWidget.class);
            int[] ids = manager.getAppWidgetIds(name);
            for (int id : ids) manager.updateAppWidget(id, build(context));
        } catch (Exception ignored) {
        }
    }

    private static RemoteViews build(Context context) {
        SharedPreferences prefs = context.getSharedPreferences(Reminders.PREFS, Context.MODE_PRIVATE);
        String raw = prefs.getString("widget_state", "");
        String[] parts = raw.split("\\|", -1);

        int done = 0, total = 0;
        try { done = Integer.parseInt(parts[0]); } catch (Exception ignored) {}
        try { total = Integer.parseInt(parts[1]); } catch (Exception ignored) {}

        RemoteViews views = new RemoteViews(context.getPackageName(), R.layout.widget_today);
        views.setTextViewText(R.id.wCount, done + " / " + total);
        int percent = total > 0 ? Math.round(done * 100f / total) : 0;
        views.setProgressBar(R.id.wBar, 100, percent, false);

        int[] lines = {R.id.wLine1, R.id.wLine2, R.id.wLine3};
        for (int i = 0; i < lines.length; i++) {
            String text = parts.length > 2 + i ? parts[2 + i] : "";
            if (text == null || text.trim().isEmpty()) {
                views.setViewVisibility(lines[i], android.view.View.GONE);
            } else {
                views.setViewVisibility(lines[i], android.view.View.VISIBLE);
                views.setTextViewText(lines[i], "• " + text);
            }
        }

        if (total > 0 && done == total) {
            views.setTextViewText(R.id.wTitle, "ALL DONE TODAY");
            views.setProgressBar(R.id.wBar, 100, 100, false);
        } else {
            views.setTextViewText(R.id.wTitle, "TODAY");
        }

        Intent open = new Intent(context, MainActivity.class);
        open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
        views.setOnClickPendingIntent(R.id.wCount,
                PendingIntent.getActivity(context, 77, open, flags));

        return views;
    }

    @Override
    public void onUpdate(Context context, AppWidgetManager manager, int[] ids) {
        for (int id : ids) manager.updateAppWidget(id, build(context));
    }
}
