package com.example.rewards

import io.kotest.matchers.shouldBe
import org.junit.jupiter.api.Test

class PointsFormatterTest {
    private val formatter = PointsFormatter()

    @Test
    fun `one point is singular`() {
        formatter.label(1) shouldBe "1 point"
    }

    @Test
    fun `several points are plural`() {
        formatter.label(5) shouldBe "5 points"
    }
}
