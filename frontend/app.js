/**
 * StudyTrack Dashboard Application Logic
 * Single-process relative fetch implementation with full event delegation.
 */

document.addEventListener("DOMContentLoaded", () => {
    // --- DOM Elements ---
    const rosterList = document.getElementById("roster-list");
    const studentForm = document.getElementById("student-form");
    const errorBanner = document.getElementById("error-banner");
    const errorMessage = document.getElementById("error-message");
    const closeErrorBtn = document.getElementById("close-error-btn");
    const rosterCountBadge = document.getElementById("roster-count-badge");
    const refreshRosterBtn = document.getElementById("refresh-roster-btn");

    // Algorithm Controls
    const sortAgeBtn = document.getElementById("sort-age-btn");
    const sortNameBtn = document.getElementById("sort-name-btn");
    const searchNameInput = document.getElementById("search-name-input");
    const searchNameBtn = document.getElementById("search-name-btn");
    const searchResultBox = document.getElementById("search-result-box");
    const minAgeInput = document.getElementById("min-age-input");
    const generateReportBtn = document.getElementById("generate-report-btn");
    const reportResultBox = document.getElementById("report-result-box");
    const reportStat = document.getElementById("report-stat");
    const reportOutput = document.getElementById("report-output");

    // AI Helper Controls
    const noteTextInput = document.getElementById("note-text-input");
    const summarizeBtn = document.getElementById("summarize-btn");
    const summaryResultBox = document.getElementById("summary-result-box");
    const summaryTopic = document.getElementById("summary-topic");
    const summaryDifficulty = document.getElementById("summary-difficulty");
    const summaryKeypoints = document.getElementById("summary-keypoints");

    const aiSearchQueryInput = document.getElementById("ai-search-query-input");
    const aiSearchBtn = document.getElementById("ai-search-btn");
    const aiSearchResults = document.getElementById("ai-search-results");

    // --- Base API URL Configuration ---
    // Relative path for same-origin single-process mode, fallback to http://localhost:8000
    const API_BASE = window.location.origin.includes("localhost") || window.location.origin.includes("127.0.0.1")
        ? ""
        : "http://localhost:8000";

    // --- Error Banner Management ---
    function showError(message) {
        errorMessage.textContent = message || "Could not reach the StudyTrack backend.";
        errorBanner.classList.remove("hidden");
    }

    function hideError() {
        errorBanner.classList.add("hidden");
    }

    if (closeErrorBtn) {
        closeErrorBtn.addEventListener("click", hideError);
    }

    // --- Helper to fetch course count for a student ---
    async function fetchCourseCount(studentId) {
        try {
            const res = await fetch(`${API_BASE}/students/${studentId}/course-count`);
            if (res.ok) {
                const data = await res.json();
                return data.course_count;
            }
        } catch (e) {
            console.warn(`Could not fetch course count for student ${studentId}`);
        }
        return 0;
    }

    // --- Student Card Construction (using document.createElement) ---
    function createStudentCardElement(student, courseCount = 0) {
        const card = document.createElement("div");
        card.className = "student-card";
        card.dataset.id = student.id;

        // Card Header (Name & Course Badge)
        const cardHeader = document.createElement("div");
        cardHeader.className = "card-header";

        const nameEl = document.createElement("h3");
        nameEl.className = "student-name";
        nameEl.textContent = student.name;

        const badgeEl = document.createElement("span");
        badgeEl.className = "course-count-badge";
        badgeEl.textContent = `${courseCount} course${courseCount === 1 ? '' : 's'}`;

        cardHeader.appendChild(nameEl);
        cardHeader.appendChild(badgeEl);

        // Student Email
        const emailEl = document.createElement("div");
        emailEl.className = "student-email";
        emailEl.textContent = student.email;

        // Card Body (Age Input & Save Button)
        const cardBody = document.createElement("div");
        cardBody.className = "card-body";

        const ageLabel = document.createElement("span");
        ageLabel.className = "age-label";
        ageLabel.textContent = "Age: ";

        const ageInput = document.createElement("input");
        ageInput.type = "number";
        ageInput.className = "age-input";
        ageInput.value = student.age;
        ageInput.min = "1";

        cardBody.appendChild(ageLabel);
        cardBody.appendChild(ageInput);

        // Card Actions (Save Age & Delete buttons)
        const cardActions = document.createElement("div");
        cardActions.className = "card-actions";

        const saveBtn = document.createElement("button");
        saveBtn.className = "btn btn-primary btn-sm save-age-btn";
        saveBtn.textContent = "Save Age";

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "btn btn-danger btn-sm delete-btn";
        deleteBtn.textContent = "Delete";

        cardActions.appendChild(saveBtn);
        cardActions.appendChild(deleteBtn);

        // Assemble card
        card.appendChild(cardHeader);
        card.appendChild(emailEl);
        card.appendChild(cardBody);
        card.appendChild(cardActions);

        return card;
    }

    // --- Render Full Roster ---
    function renderRosterList(studentsList) {
        rosterList.innerHTML = ""; // Clear list
        if (!studentsList || studentsList.length === 0) {
            const emptyMsg = document.createElement("p");
            emptyMsg.style.color = "var(--text-muted)";
            emptyMsg.style.padding = "20px";
            emptyMsg.textContent = "No student records found in roster.";
            rosterList.appendChild(emptyMsg);
            rosterCountBadge.textContent = "0 Students";
            return;
        }

        rosterCountBadge.textContent = `${studentsList.length} Student${studentsList.length === 1 ? '' : 's'}`;

        studentsList.forEach(async (student) => {
            const courseCount = await fetchCourseCount(student.id);
            const cardEl = createStudentCardElement(student, courseCount);
            rosterList.appendChild(cardEl);
        });
    }

    // --- Task 10: Fetch Roster on Page Load ---
    async function loadRoster() {
        hideError();
        try {
            const response = await fetch(`${API_BASE}/students/`);
            if (!response.ok) {
                showError("Could not reach the StudyTrack backend. (HTTP " + response.status + ")");
                return;
            }
            const students = await response.json();
            renderRosterList(students);
        } catch (err) {
            console.error("Error loading roster:", err);
            showError("Could not reach the StudyTrack backend. Please ensure server is running.");
        }
    }

    // --- Task 11: Single Event Listener on #roster-list (EVENT DELEGATION) ---
    rosterList.addEventListener("click", async (event) => {
        const target = event.target;
        const card = target.closest(".student-card");
        if (!card) return;

        const studentId = card.dataset.id;

        // 11a: Click on "Save Age" button
        if (target.classList.contains("save-age-btn")) {
            const ageInput = card.querySelector(".age-input");
            const newAge = parseInt(ageInput.value, 10);

            if (isNaN(newAge) || newAge <= 0) {
                showError("Please enter a valid positive age.");
                return;
            }

            hideError();
            try {
                const response = await fetch(`${API_BASE}/students/${studentId}`, {
                    method: "PATCH",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ age: newAge })
                });

                if (!response.ok) {
                    const errData = await response.json().catch(() => ({}));
                    showError(errData.detail || "Failed to update student age.");
                    return;
                }

                const updatedStudent = await response.json();
                ageInput.value = updatedStudent.age;
                
                // Visual confirmation toast on button
                const origText = target.textContent;
                target.textContent = "Saved ✓";
                target.style.background = "var(--success)";
                setTimeout(() => {
                    target.textContent = origText;
                    target.style.background = "";
                }, 1500);

            } catch (err) {
                console.error("Error patching age:", err);
                showError("Could not reach the StudyTrack backend.");
            }
        }

        // 11b: Click on "Delete" button
        if (target.classList.contains("delete-btn")) {
            if (!confirm("Are you sure you want to delete this student?")) return;

            hideError();
            try {
                const response = await fetch(`${API_BASE}/students/${studentId}`, {
                    method: "DELETE"
                });

                if (!response.ok) {
                    showError("Failed to delete student record.");
                    return;
                }

                // Remove element from DOM on success
                card.remove();

                // Update count badge
                const remainingCards = rosterList.querySelectorAll(".student-card").length;
                rosterCountBadge.textContent = `${remainingCards} Student${remainingCards === 1 ? '' : 's'}`;

            } catch (err) {
                console.error("Error deleting student:", err);
                showError("Could not reach the StudyTrack backend.");
            }
        }
    });

    // --- Task 12: Wire #student-form submit handler ---
    studentForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        hideError();

        const nameInput = document.getElementById("student-name");
        const emailInput = document.getElementById("student-email");
        const ageInput = document.getElementById("student-age");

        const studentData = {
            name: nameInput.value.trim(),
            email: emailInput.value.trim(),
            age: parseInt(ageInput.value, 10)
        };

        try {
            const response = await fetch(`${API_BASE}/students/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(studentData)
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                const msg = Array.isArray(errData.detail)
                    ? errData.detail.map(d => d.msg).join(", ")
                    : (errData.detail || "Failed to create student.");
                showError(msg);
                return;
            }

            const newStudent = await response.json();

            // Create and append new student card to DOM directly
            const newCard = createStudentCardElement(newStudent, 0);
            rosterList.appendChild(newCard);

            // Update badge count
            const cardCount = rosterList.querySelectorAll(".student-card").length;
            rosterCountBadge.textContent = `${cardCount} Student${cardCount === 1 ? '' : 's'}`;

            // Reset form
            studentForm.reset();

        } catch (err) {
            console.error("Error creating student:", err);
            showError("Could not reach the StudyTrack backend.");
        }
    });

    if (refreshRosterBtn) {
        refreshRosterBtn.addEventListener("click", loadRoster);
    }

    // ======================================================
    // PART 2: ALGORITHMS ENGINE FRONTEND HANDLERS
    // ======================================================

    // Insertion Sort handlers
    async function fetchSortedRoster(byField) {
        hideError();
        try {
            const response = await fetch(`${API_BASE}/students/sorted?by=${byField}`);
            if (!response.ok) {
                showError("Failed to fetch sorted roster.");
                return;
            }
            const sortedStudents = await response.json();
            renderRosterList(sortedStudents);
        } catch (err) {
            showError("Could not reach the StudyTrack backend.");
        }
    }

    if (sortAgeBtn) sortAgeBtn.addEventListener("click", () => fetchSortedRoster("age"));
    if (sortNameBtn) sortNameBtn.addEventListener("click", () => fetchSortedRoster("name"));

    // Binary Search handler
    if (searchNameBtn) {
        searchNameBtn.addEventListener("click", async () => {
            const queryName = searchNameInput.value.trim();
            if (!queryName) return;

            hideError();
            searchResultBox.classList.add("hidden");

            try {
                const response = await fetch(`${API_BASE}/students/search?name=${encodeURIComponent(queryName)}`);
                searchResultBox.classList.remove("hidden");

                if (response.status === 404) {
                    searchResultBox.innerHTML = `<p style="color:#fca5a5;">❌ Student "${queryName}" not found in roster.</p>`;
                    return;
                }

                if (!response.ok) {
                    showError("Binary search query failed.");
                    return;
                }

                const result = await response.json();
                searchResultBox.innerHTML = `
                    <div style="color: var(--success); font-weight:600; margin-bottom:4px;">✓ Match Found (Binary Search):</div>
                    <div style="font-size:0.9rem;">
                        <strong>${result.name}</strong> (${result.email}) — Age: <strong>${result.age}</strong> (ID: ${result.id})
                    </div>
                `;

            } catch (err) {
                showError("Could not reach the StudyTrack backend.");
            }
        });
    }

    // Roster Report handler
    if (generateReportBtn) {
        generateReportBtn.addEventListener("click", async () => {
            const minAge = minAgeInput.value || 21;
            hideError();
            reportResultBox.classList.add("hidden");

            try {
                const response = await fetch(`${API_BASE}/students/report?min_age=${minAge}`);
                if (!response.ok) {
                    showError("Failed to generate roster report.");
                    return;
                }

                const data = await response.json();
                reportResultBox.classList.remove("hidden");
                reportStat.textContent = `Students meeting min age (${minAge}+): ${data.count_meeting_min_age}`;
                reportOutput.textContent = data.report;

            } catch (err) {
                showError("Could not reach the StudyTrack backend.");
            }
        });
    }

    // ======================================================
    // PART 3: AI ASSISTANT FRONTEND HANDLERS
    // ======================================================

    // Note Summarizer Handler
    if (summarizeBtn) {
        summarizeBtn.addEventListener("click", async () => {
            const text = noteTextInput.value;
            hideError();
            summaryResultBox.classList.add("hidden");

            try {
                const response = await fetch(`${API_BASE}/assistant/summarize`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text: text })
                });

                if (!response.ok) {
                    showError("AI Summarization request failed.");
                    return;
                }

                const data = await response.json();
                summaryResultBox.classList.remove("hidden");

                summaryTopic.textContent = data.topic;
                summaryDifficulty.textContent = data.difficulty;
                summaryDifficulty.className = `badge-difficulty badge-${data.difficulty}`;

                summaryKeypoints.innerHTML = "";
                if (data.key_points.length === 0) {
                    const li = document.createElement("li");
                    li.textContent = "No key points extracted.";
                    summaryKeypoints.appendChild(li);
                } else {
                    data.key_points.forEach(kp => {
                        const li = document.createElement("li");
                        li.textContent = kp;
                        summaryKeypoints.appendChild(li);
                    });
                }

            } catch (err) {
                showError("Could not reach the StudyTrack backend.");
            }
        });
    }

    // Semantic Search Handler
    async function performAiSearch() {
        const query = aiSearchQueryInput.value.trim();
        hideError();
        aiSearchResults.innerHTML = "<p style='color:var(--text-muted); font-size:0.85rem;'>Searching...</p>";

        try {
            const response = await fetch(`${API_BASE}/assistant/search?query=${encodeURIComponent(query)}`);
            if (!response.ok) {
                showError("AI Search request failed.");
                return;
            }

            const notesList = await response.json();
            aiSearchResults.innerHTML = "";

            if (!notesList || notesList.length === 0) {
                aiSearchResults.innerHTML = "<p style='color:var(--text-muted);'>No notes found.</p>";
                return;
            }

            notesList.forEach(note => {
                const item = document.createElement("div");
                item.className = "search-note-item";

                const scoreTag = document.createElement("span");
                scoreTag.className = "note-score-tag";
                scoreTag.textContent = `Score: ${note.score.toFixed(4)} (ID: ${note.id})`;

                const bodyText = document.createElement("div");
                bodyText.className = "note-text-body";
                bodyText.textContent = note.text;

                item.appendChild(scoreTag);
                item.appendChild(bodyText);
                aiSearchResults.appendChild(item);
            });

        } catch (err) {
            showError("Could not reach the StudyTrack backend.");
        }
    }

    if (aiSearchBtn) {
        aiSearchBtn.addEventListener("click", performAiSearch);
    }

    // --- Initial Load ---
    loadRoster();
    performAiSearch(); // Initial load of default semantic search results
});
