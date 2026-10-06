package com.example.ledgerly.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.example.ledgerly.ui.theme.Spacing

@Composable
fun HomeScreen(weeklyMargin: String, unpaidInvoices: Int, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier.fillMaxSize().padding(Spacing.md),
        verticalArrangement = Arrangement.spacedBy(Spacing.md),
    ) {
        Text("This week", style = MaterialTheme.typography.headlineSmall)
        Card(shape = MaterialTheme.shapes.medium) {
            Column(Modifier.padding(Spacing.md), verticalArrangement = Arrangement.spacedBy(Spacing.xs)) {
                Text("Margin", style = MaterialTheme.typography.titleMedium)
                Text(weeklyMargin, style = MaterialTheme.typography.bodyMedium)
            }
        }
        Card(shape = MaterialTheme.shapes.medium) {
            Column(Modifier.padding(Spacing.md), verticalArrangement = Arrangement.spacedBy(Spacing.xs)) {
                Text("Unpaid invoices", style = MaterialTheme.typography.titleMedium)
                Text(
                    "$unpaidInvoices waiting",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.tertiary,
                )
            }
        }
    }
}
