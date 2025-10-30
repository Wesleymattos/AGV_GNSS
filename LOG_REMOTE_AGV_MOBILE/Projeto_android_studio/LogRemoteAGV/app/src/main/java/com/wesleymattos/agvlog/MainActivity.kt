package com.wesleymattos.agvlog

import android.os.Bundle
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    private var webview: WebView? = null

    @Override
    protected fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webview = findViewById(R.id.webview)
        webview.setWebViewClient(WebViewClient())

        val webSettings: WebSettings = webview.getSettings()
        webSettings.setJavaScriptEnabled(true)

        webview.loadUrl("https://wesleymattos.github.io/AGV_GNSS/")
    }

    @Override
    fun onBackPressed() {
        if (webview.canGoBack()) {
            webview.goBack()
        } else {
            super.onBackPressed()
        }
    }
}