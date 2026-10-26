package com.iflytek.rpa.base.service.impl;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;

import java.time.Duration;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import org.junit.jupiter.api.Test;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;

class SemanticChoiceCapabilitiesTest {
    private static final String URL = "http://ai-service:8010/v1/decision/capabilities";
    private final AtomicLong clock = new AtomicLong();
    private final SemanticChoiceCapabilities capabilities =
            new SemanticChoiceCapabilities(new RestTemplateBuilder(), URL, clock::get);
    private final RestTemplate rest =
            (RestTemplate) org.springframework.test.util.ReflectionTestUtils.getField(capabilities, "restTemplate");
    private final MockRestServiceServer server =
            MockRestServiceServer.bindTo(rest).build();

    @Test
    void acceptsOnlyExplicitBooleanEnabled() {
        for (String body :
                new String[] {"{\"enabled\":true}", "{\"enabled\":false}", "{}", "{\"enabled\":\"true\"}", "invalid"}) {
            clock.addAndGet(Duration.ofSeconds(30).toNanos());
            server.reset();
            server.expect(requestTo(URL)).andRespond(withSuccess(body, MediaType.APPLICATION_JSON));
            assertEquals(body.equals("{\"enabled\":true}"), capabilities.isEnabled());
            server.verify();
        }
    }

    @Test
    void reusesEnabledResult() {
        server.expect(requestTo(URL)).andRespond(withSuccess("{\"enabled\":true}", MediaType.APPLICATION_JSON));
        assertTrue(capabilities.isEnabled());
        assertTrue(capabilities.isEnabled());
        server.verify();
    }

    @Test
    void reusesFailedResult() {
        server.expect(requestTo(URL)).andRespond(withServerError());
        assertFalse(capabilities.isEnabled());
        assertFalse(capabilities.isEnabled());
        server.verify();
    }

    @Test
    void refreshesAtExpiryAndDoesNotServeStaleEnabledOnFailure() {
        server.expect(requestTo(URL)).andRespond(withSuccess("{\"enabled\":true}", MediaType.APPLICATION_JSON));
        server.expect(requestTo(URL)).andRespond(withServerError());
        server.expect(requestTo(URL)).andRespond(withSuccess("{\"enabled\":true}", MediaType.APPLICATION_JSON));
        assertTrue(capabilities.isEnabled());
        clock.set(Duration.ofSeconds(30).toNanos() - 1);
        assertTrue(capabilities.isEnabled());
        clock.incrementAndGet();
        assertFalse(capabilities.isEnabled());
        assertFalse(capabilities.isEnabled());
        clock.addAndGet(Duration.ofSeconds(30).toNanos());
        assertTrue(capabilities.isEnabled());
        server.verify();
    }

    @Test
    void cachesDisabledAndInvalidResponses() {
        for (String body : new String[] {"{\"enabled\":false}", "{}", "invalid"}) {
            server.reset();
            clock.addAndGet(Duration.ofSeconds(30).toNanos());
            server.expect(requestTo(URL)).andRespond(withSuccess(body, MediaType.APPLICATION_JSON));
            assertFalse(capabilities.isEnabled());
            assertFalse(capabilities.isEnabled());
            server.verify();
        }
    }

    @Test
    void concurrentCallersShareOneRefresh() throws Exception {
        ExecutorService executor = Executors.newFixedThreadPool(8);
        try {
            // Cold load, failed refresh after expiry, then recovery after expiry.
            for (boolean enabled : new boolean[] {true, false, true}) {
                server.reset();
                clock.addAndGet(Duration.ofSeconds(30).toNanos());
                CountDownLatch requestStarted = new CountDownLatch(1);
                CountDownLatch releaseResponse = new CountDownLatch(1);
                server.expect(requestTo(URL)).andRespond(request -> {
                    requestStarted.countDown();
                    try {
                        if (!releaseResponse.await(5, TimeUnit.SECONDS)) {
                            throw new AssertionError("Response was not released");
                        }
                    } catch (InterruptedException exception) {
                        Thread.currentThread().interrupt();
                        throw new AssertionError(exception);
                    }
                    return enabled
                            ? withSuccess("{\"enabled\":true}", MediaType.APPLICATION_JSON)
                                    .createResponse(request)
                            : withServerError().createResponse(request);
                });
                java.util.List<Future<Boolean>> results = new java.util.ArrayList<>();
                java.util.List<Thread> waitingThreads = new java.util.concurrent.CopyOnWriteArrayList<>();
                CountDownLatch callersStarted = new CountDownLatch(7);
                try {
                    results.add(executor.submit(capabilities::isEnabled));
                    assertTrue(requestStarted.await(5, TimeUnit.SECONDS));
                    for (int i = 0; i < 7; i++) {
                        results.add(executor.submit(() -> {
                            waitingThreads.add(Thread.currentThread());
                            callersStarted.countDown();
                            return capabilities.isEnabled();
                        }));
                    }
                    assertTrue(callersStarted.await(5, TimeUnit.SECONDS));
                    // Wait until every follower has actually reached the synchronized lookup.
                    // A start barrier alone could let the response finish before followers run.
                    long deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(2);
                    while (waitingThreads.stream().anyMatch(thread -> thread.getState() != Thread.State.BLOCKED)
                            && System.nanoTime() < deadline) {
                        Thread.sleep(1);
                    }
                    assertTrue(waitingThreads.stream().allMatch(thread -> thread.getState() == Thread.State.BLOCKED));
                    assertTrue(results.stream().noneMatch(Future::isDone));
                } finally {
                    releaseResponse.countDown();
                }
                for (Future<Boolean> result : results) {
                    assertEquals(enabled, result.get(5, TimeUnit.SECONDS));
                }
                assertEquals(enabled, capabilities.isEnabled());
                server.verify();
            }
        } finally {
            executor.shutdownNow();
            assertTrue(executor.awaitTermination(5, TimeUnit.SECONDS));
        }
    }

    @Test
    void serviceFailureDisablesCapability() {
        server.expect(requestTo(URL)).andRespond(withServerError());
        assertFalse(capabilities.isEnabled());
    }

    @Test
    void timeoutDisablesCapability() {
        server.expect(requestTo(URL)).andRespond(request -> {
            throw new java.net.SocketTimeoutException("timeout");
        });
        assertFalse(capabilities.isEnabled());
    }
}
