package com.example.rewards

/** Builds the label the rewards tile shows under the balance. */
class PointsFormatter {
    fun label(points: Int): String = if (points > 1) "$points points" else "$points point"
}
