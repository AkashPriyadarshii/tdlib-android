package io.github.tdlibandroid.ktx

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class TdExceptionTest {

    @Test
    fun testFloodWaitParsing() {
        val ex = TdException(code = 429, message = "FLOOD_WAIT_42")
        assertTrue(ex.isFloodWait)
        assertEquals(42L, ex.floodWaitSeconds)
        assertFalse(ex.isUnauthorized)
    }

    @Test
    fun testNonFloodWaitException() {
        val ex = TdException(code = 400, message = "PHONE_NUMBER_INVALID")
        assertFalse(ex.isFloodWait)
        assertEquals(0L, ex.floodWaitSeconds)
        assertFalse(ex.isUnauthorized)
    }

    @Test
    fun testUnauthorizedException() {
        val ex = TdException(code = 401, message = "Unauthorized")
        assertFalse(ex.isFloodWait)
        assertEquals(0L, ex.floodWaitSeconds)
        assertTrue(ex.isUnauthorized)
    }

    @Test
    fun testMalformedFloodWaitMessage() {
        val ex = TdException(code = 429, message = "FLOOD_WAIT_INVALID_NUMBER")
        assertTrue(ex.isFloodWait)
        assertEquals(0L, ex.floodWaitSeconds)
    }
}
