package com.example.ledgerly.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LightColors = lightColorScheme(
    primary = Teal,
    onPrimary = OnTeal,
    background = Parchment,
    surface = Parchment,
    onSurface = Ink,
    tertiary = Clay,
)

private val DarkColors = darkColorScheme(
    primary = TealLight,
    onPrimary = Ink,
    background = InkDeep,
    surface = InkDeep,
    onSurface = Parchment,
    tertiary = Clay,
)

@Composable
fun LedgerlyTheme(darkTheme: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        typography = LedgerlyTypography,
        shapes = LedgerlyShapes,
        content = content,
    )
}
