package com.iflytek.rpa.example.entity.Dto;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import org.junit.jupiter.api.Test;

class WorkflowsUpsertDtoTest {

    @Test
    void shouldCreateAnActivePublishedWorkflow() {
        WorkflowsUpsertDto workflow = WorkflowsUpsertDto.published("robot-1", "Invoice Bot", "", 3, "[]", null);

        assertEquals("robot-1", workflow.getProject_id());
        assertEquals("Invoice Bot", workflow.getName());
        assertEquals("Invoice Bot", workflow.getEnglish_name());
        assertEquals("", workflow.getDescription());
        assertEquals(3, workflow.getVersion());
        assertEquals(1, workflow.getStatus());
        assertEquals("[]", workflow.getParameters());
        assertNull(workflow.getExample_project_id());
    }

    @Test
    void shouldUseProjectIdWhenPublishedWorkflowNameIsUnavailable() {
        WorkflowsUpsertDto workflow = WorkflowsUpsertDto.published("robot-2", " ", "", 1, "[]", null);

        assertEquals("robot-2", workflow.getName());
        assertEquals("robot-2", workflow.getEnglish_name());
    }

    @Test
    void shouldPreserveExampleProjectMapping() {
        WorkflowsUpsertDto workflow =
                WorkflowsUpsertDto.published("robot-3", null, "Imported workflow", 2, "[]", "example-robot-3");

        assertEquals("robot-3", workflow.getName());
        assertEquals("Imported workflow", workflow.getDescription());
        assertEquals("example-robot-3", workflow.getExample_project_id());
    }
}
