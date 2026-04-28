const API_BASE = "http://127.0.0.1:5000/api";

const state = {
    students: [],
    guardians: [],
    relationships: [],
    enrollments: [],
    programHistory: [],
    programs: [],
    subjects: [],
    curriculums: [],
    sections: [],
    instructors: [],
    schedules: [],
    classOfferings: [],
    classSchedules: []
};

const editing = {
    students: null,
    guardians: null,
    relationships: null,
    enrollments: null,
    programHistory: null,
    programs: null,
    subjects: null,
    curriculums: null,
    sections: null,
    instructors: null,
    schedules: null,
    classOfferings: null,
    classSchedules: null
};

const idFields = {
    students: "student_id",
    guardians: "guardian_id",
    relationships: "relationship_id",
    enrollments: "enrollment_id",
    programHistory: "history_id",
    programs: "program_id",
    subjects: "subject_code",
    curriculums: "curriculum_id",
    sections: "section_id",
    instructors: "instructor_id",
    schedules: "schedule_id",
    classOfferings: "class_offering_id",
    classSchedules: "class_schedule_id"
};

const modalConfig = {
    students: { modalId: "studentFormModal", saveButtonId: "saveStudent", closeButtonId: "closeStudentForm", title: "Student" },
    guardians: { modalId: "guardianFormModal", saveButtonId: "saveGuardian", closeButtonId: "closeGuardianForm", title: "Guardian" },
    relationships: { modalId: "relationshipFormModal", saveButtonId: "saveRelationship", closeButtonId: "closeRelationshipForm", title: "Relationship" },
    enrollments: { modalId: "enrollmentFormModal", saveButtonId: "saveEnrollment", closeButtonId: "closeEnrollmentForm", title: "Enrollment" },
    programHistory: { modalId: "programHistoryFormModal", saveButtonId: "saveProgramHistory", closeButtonId: "closeProgramHistoryForm", title: "Program History" },
    programs: { modalId: "programFormModal", saveButtonId: "saveProgram", closeButtonId: "closeProgramForm", title: "Program" },
    subjects: { modalId: "subjectFormModal", saveButtonId: "saveSubject", closeButtonId: "closeSubjectForm", title: "Subject" },
    curriculums: { modalId: "curriculumFormModal", saveButtonId: "saveCurriculum", closeButtonId: "closeCurriculumForm", title: "Curriculum" },
    sections: { modalId: "sectionFormModal", saveButtonId: "saveSection", closeButtonId: "closeSectionForm", title: "Section" },
    instructors: { modalId: "instructorFormModal", saveButtonId: "saveInstructor", closeButtonId: "closeInstructorForm", title: "Instructor" },
    schedules: { modalId: "scheduleFormModal", saveButtonId: "saveSchedule", closeButtonId: "closeScheduleForm", title: "Schedule" },
    classOfferings: { modalId: "classOfferingFormModal", saveButtonId: "saveClassOffering", closeButtonId: "closeClassOfferingForm", title: "Class Offering" },
    classSchedules: { modalId: "classScheduleFormModal", saveButtonId: "saveClassSchedule", closeButtonId: "closeClassScheduleForm", title: "Class Schedule" }
};

let backendAlertShown = false;

function byId(id) {
    return document.getElementById(id);
}

function valueOf(id) {
    const element = byId(id);
    return element ? element.value.trim() : "";
}

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function fullName(first, middle, last) {
    return [first, middle, last].filter(Boolean).join(" ");
}

function programLabel(program) {
    return [program?.program_name, program?.major].filter(Boolean).join(" - ");
}

function formatTime(value) {
    if (!value) return "";
    const [hourText, minute = "00"] = String(value).split(":");
    let hour = Number(hourText);
    if (Number.isNaN(hour)) return String(value);
    const suffix = hour >= 12 ? "PM" : "AM";
    hour = hour % 12 || 12;
    return `${hour}:${minute} ${suffix}`;
}

function scheduleLabel(schedule) {
    const day = schedule?.day || "";
    const start = formatTime(schedule?.time_start);
    const end = formatTime(schedule?.time_end);
    return `${day} ${start}${end ? `-${end}` : ""}`.trim();
}

function studentLabel(student) {
    return `${student.lrn || student.student_id} - ${fullName(student.first_name, student.middle_name, student.last_name)}`;
}

function classOfferingLabel(offering) {
    const subject = [offering.subject_code, offering.subject_title].filter(Boolean).join(" - ");
    return `${subject || "Class"} | ${offering.section_name || "No section"} | ${offering.room || "No room"} | ${offering.school_year || ""} ${offering.sem || ""}`.trim();
}

function display(value, fallback = "-") {
    return escapeHtml(value || fallback);
}

async function apiFetch(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    const text = await response.text();
    let data = {};

    try {
        data = text ? JSON.parse(text) : {};
    } catch {
        data = { error: text || "Request failed." };
    }

    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }

    return data;
}

function handleLoadError(error) {
    console.error(error);
    if (!backendAlertShown) {
        alert(`Cannot connect to the backend or database: ${error.message}`);
        backendAlertShown = true;
    }
}

function filterRows(rows, selectors, searchValue) {
    const value = (searchValue || "").toLowerCase();
    if (!value) return rows;

    return rows.filter(row =>
        selectors.some(selector => {
            const fieldValue = typeof selector === "function" ? selector(row) : row[selector];
            return String(fieldValue ?? "").toLowerCase().includes(value);
        })
    );
}

function renderFiltered(collectionName, inputId, renderer, selectors) {
    renderer(filterRows(state[collectionName], selectors, valueOf(inputId)));
}

function option(value, label) {
    const element = document.createElement("option");
    element.value = value ?? "";
    element.textContent = label || "";
    return element;
}

function resetModal(modal) {
    if (!modal) return;
    modal.querySelectorAll("input, select").forEach(element => {
        element.value = "";
    });
}

function showModal(modal) {
    if (modal) modal.style.display = "flex";
}

function hideModal(modal) {
    if (modal) modal.style.display = "none";
}

function setModalMode(entityKey, recordId) {
    editing[entityKey] = recordId ?? null;
    const config = modalConfig[entityKey];
    const modal = byId(config.modalId);
    const title = modal?.querySelector("h3");
    const saveButton = byId(config.saveButtonId);

    if (title) {
        title.textContent = `${recordId !== null && recordId !== undefined ? "Edit" : "Add"} ${config.title}`;
    }

    if (saveButton) {
        saveButton.textContent = recordId !== null && recordId !== undefined ? "Update" : "Save";
    }

    if (entityKey === "subjects") {
        const subjectCode = byId("subCode");
        if (subjectCode) subjectCode.disabled = recordId !== null && recordId !== undefined;
    }

    return modal;
}

function closeEntityModal(entityKey) {
    const config = modalConfig[entityKey];
    const modal = byId(config.modalId);
    editing[entityKey] = null;
    resetModal(modal);
    hideModal(modal);

    if (entityKey === "subjects") {
        const subjectCode = byId("subCode");
        if (subjectCode) subjectCode.disabled = false;
    }

    setModalMode(entityKey, null);
}

function getRecord(collectionName, id) {
    const idField = idFields[collectionName];
    return state[collectionName].find(row => String(row[idField]) === String(id));
}

function buildActionButtons(entity, id) {
    return `
        <div class="tableActions">
            <button type="button" class="actionButton" onclick='handleEdit(${JSON.stringify(entity)}, ${JSON.stringify(id)})'>Edit</button>
            <button type="button" class="actionButton deleteAction" onclick='handleDelete(${JSON.stringify(entity)}, ${JSON.stringify(id)})'>Delete</button>
        </div>
    `;
}

function renderEmpty(table, colSpan, label) {
    table.innerHTML = `<tr><td colspan="${colSpan}">No ${escapeHtml(label)} found.</td></tr>`;
}

function renderStudents(rows) {
    const table = byId("studentsTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 10, "students");

    table.innerHTML = rows.map((student, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(student.lrn)}</td>
            <td>${display(programLabel(student))}</td>
            <td>${escapeHtml(fullName(student.first_name, student.middle_name, student.last_name))}</td>
            <td>${escapeHtml(student.birthdate || "")}</td>
            <td>${escapeHtml(student.gender || "")}</td>
            <td>${escapeHtml(student.address || "")}</td>
            <td>${escapeHtml(student.contact_no || "")}</td>
            <td>${display(student.guardian_name)}</td>
            <td>${buildActionButtons("students", student.student_id)}</td>
        </tr>
    `).join("");
}

function renderGuardians(rows) {
    const table = byId("guardiansTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 4, "guardians");

    table.innerHTML = rows.map((guardian, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(fullName(guardian.first_name, guardian.middle_name, guardian.last_name))}</td>
            <td>${escapeHtml(guardian.contact_number || "")}</td>
            <td>${buildActionButtons("guardians", guardian.guardian_id)}</td>
        </tr>
    `).join("");
}

function renderRelationships(rows) {
    const table = byId("relationshipsTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 5, "relationships");

    table.innerHTML = rows.map((relationship, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(relationship.student_name)}</td>
            <td>${escapeHtml(relationship.guardian_name)}</td>
            <td>${escapeHtml(relationship.relationship_type)}</td>
            <td>${buildActionButtons("relationships", relationship.relationship_id)}</td>
        </tr>
    `).join("");
}

function renderEnrollments(rows) {
    const table = byId("enrollmentsTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 8, "enrollments");

    table.innerHTML = rows.map((enrollment, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(enrollment.student_name)}</td>
            <td>${display([enrollment.subject_code, enrollment.subject_title].filter(Boolean).join(" - ") || enrollment.room)}</td>
            <td>${display(enrollment.section_name)}</td>
            <td>${escapeHtml(enrollment.school_year || "")}</td>
            <td>${escapeHtml(enrollment.sem || "")}</td>
            <td>${escapeHtml(enrollment.enrollment_timestamp || "")}</td>
            <td>${buildActionButtons("enrollments", enrollment.enrollment_id)}</td>
        </tr>
    `).join("");
}

function renderProgramHistory(rows) {
    const table = byId("programHistoryTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 7, "program history records");

    table.innerHTML = rows.map((history, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(history.student_name)}</td>
            <td>${display(programLabel(history))}</td>
            <td>${escapeHtml(history.school_year || "")}</td>
            <td>${escapeHtml(history.semester || "")}</td>
            <td>${escapeHtml(history.status || "")}</td>
            <td>${buildActionButtons("programHistory", history.history_id)}</td>
        </tr>
    `).join("");
}

function renderPrograms(rows) {
    const table = byId("programsTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 4, "programs");

    table.innerHTML = rows.map((program, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(program.program_name)}</td>
            <td>${escapeHtml(program.major || "")}</td>
            <td>${buildActionButtons("programs", program.program_id)}</td>
        </tr>
    `).join("");
}

function renderSubjects(rows) {
    const table = byId("subjectsTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 6, "subjects");

    table.innerHTML = rows.map((subject, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(subject.subject_code)}</td>
            <td>${escapeHtml(subject.title)}</td>
            <td>${escapeHtml(subject.units)}</td>
            <td>${display(subject.prerequisite_code)}</td>
            <td>${buildActionButtons("subjects", subject.subject_code)}</td>
        </tr>
    `).join("");
}

function renderCurriculums(rows) {
    const table = byId("curriculumsTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 6, "curriculums");

    table.innerHTML = rows.map((curriculum, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${display(programLabel(curriculum))}</td>
            <td>${display([curriculum.subject_code, curriculum.subject_title].filter(Boolean).join(" - "))}</td>
            <td>${escapeHtml(curriculum.year_level)}</td>
            <td>${escapeHtml(curriculum.semester)}</td>
            <td>${buildActionButtons("curriculums", curriculum.curriculum_id)}</td>
        </tr>
    `).join("");
}

function renderSections(rows) {
    const table = byId("sectionsTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 3, "sections");

    table.innerHTML = rows.map((section, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(section.section_name)}</td>
            <td>${buildActionButtons("sections", section.section_id)}</td>
        </tr>
    `).join("");
}

function renderInstructors(rows) {
    const table = byId("instructorsTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 5, "instructors");

    table.innerHTML = rows.map((instructor, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(instructor.name)}</td>
            <td>${escapeHtml(instructor.department || "")}</td>
            <td>${escapeHtml(instructor.contact_number || "")}</td>
            <td>${buildActionButtons("instructors", instructor.instructor_id)}</td>
        </tr>
    `).join("");
}

function renderSchedules(rows) {
    const table = byId("schedulesTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 5, "schedules");

    table.innerHTML = rows.map((schedule, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(schedule.day)}</td>
            <td>${escapeHtml(formatTime(schedule.time_start))}</td>
            <td>${escapeHtml(formatTime(schedule.time_end))}</td>
            <td>${buildActionButtons("schedules", schedule.schedule_id)}</td>
        </tr>
    `).join("");
}

function renderClassOfferings(rows) {
    const table = byId("offeringsTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 9, "class offerings");

    table.innerHTML = rows.map((offering, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${escapeHtml(offering.room)}</td>
            <td>${display(offering.section_name)}</td>
            <td>${display([offering.subject_code, offering.subject_title].filter(Boolean).join(" - "))}</td>
            <td>${display(scheduleLabel(offering))}</td>
            <td>${display(offering.instructor_name)}</td>
            <td>${escapeHtml(offering.school_year || "")}</td>
            <td>${escapeHtml(offering.sem || "")}</td>
            <td>${buildActionButtons("classOfferings", offering.class_offering_id)}</td>
        </tr>
    `).join("");
}

function renderClassSchedules(rows) {
    const table = byId("classSchedulesTable");
    if (!table) return;
    if (!rows.length) return renderEmpty(table, 7, "class schedules");

    table.innerHTML = rows.map((classSchedule, index) => `
        <tr>
            <td>${index + 1}</td>
            <td>${display([classSchedule.subject_code, classSchedule.subject_title].filter(Boolean).join(" - ") || classSchedule.room)}</td>
            <td>${display(classSchedule.section_name)}</td>
            <td>${display(scheduleLabel(classSchedule))}</td>
            <td>${escapeHtml(classSchedule.school_year || "")}</td>
            <td>${escapeHtml(classSchedule.sem || "")}</td>
            <td>${buildActionButtons("classSchedules", classSchedule.class_schedule_id)}</td>
        </tr>
    `).join("");
}

async function loadStudents() {
    state.students = await apiFetch("/students");
    renderFiltered("students", "searchStudentBar", renderStudents, [
        "lrn",
        "program_name",
        "major",
        row => fullName(row.first_name, row.middle_name, row.last_name),
        "guardian_name"
    ]);
}

async function loadGuardians() {
    state.guardians = await apiFetch("/guardians");
    renderFiltered("guardians", "searchGuardianBar", renderGuardians, [
        row => fullName(row.first_name, row.middle_name, row.last_name),
        "contact_number"
    ]);
}

async function loadRelationships() {
    state.relationships = await apiFetch("/relationships");
    renderFiltered("relationships", "searchRelationshipBar", renderRelationships, [
        "student_name",
        "guardian_name",
        "relationship_type"
    ]);
}

async function loadEnrollments() {
    state.enrollments = await apiFetch("/enrollments");
    renderFiltered("enrollments", "searchEnrollmentBar", renderEnrollments, [
        "student_name",
        "subject_code",
        "subject_title",
        "section_name",
        "school_year",
        "sem"
    ]);
}

async function loadProgramHistory() {
    state.programHistory = await apiFetch("/program-history");
    renderFiltered("programHistory", "searchProgramHistoryBar", renderProgramHistory, [
        "student_name",
        "program_name",
        "major",
        "school_year",
        "semester",
        "status"
    ]);
}

async function loadPrograms() {
    state.programs = await apiFetch("/programs");
    renderFiltered("programs", "searchProgram", renderPrograms, ["program_name", "major"]);
}

async function loadSubjects() {
    state.subjects = await apiFetch("/subjects");
    renderFiltered("subjects", "searchSubjectBar", renderSubjects, ["subject_code", "title", "prerequisite_code"]);
}

async function loadCurriculums() {
    state.curriculums = await apiFetch("/curriculums");
    renderFiltered("curriculums", "searchCurriculumBar", renderCurriculums, [
        "program_name",
        "major",
        "subject_code",
        "subject_title",
        "year_level",
        "semester"
    ]);
}

async function loadSections() {
    state.sections = await apiFetch("/sections");
    renderFiltered("sections", "searchSectionBar", renderSections, ["section_name"]);
}

async function loadInstructors() {
    state.instructors = await apiFetch("/instructors");
    renderFiltered("instructors", "searchInstructorBar", renderInstructors, ["name", "department"]);
}

async function loadSchedules() {
    state.schedules = await apiFetch("/schedules");
    renderFiltered("schedules", "searchScheduleBar", renderSchedules, ["day", "time_start", "time_end"]);
}

async function loadClassOfferings() {
    state.classOfferings = await apiFetch("/class-offerings");
    renderFiltered("classOfferings", "searchClassOffering", renderClassOfferings, [
        "room",
        "section_name",
        "subject_code",
        "subject_title",
        "instructor_name",
        "school_year",
        "sem"
    ]);
}

async function loadClassSchedules() {
    state.classSchedules = await apiFetch("/class-schedules");
    renderFiltered("classSchedules", "searchClassScheduleBar", renderClassSchedules, [
        "room",
        "section_name",
        "subject_code",
        "subject_title",
        "school_year",
        "sem",
        "day"
    ]);
}

function populateStudentDropdowns() {
    const programSelect = byId("program");
    const guardianSelect = byId("studentGuardianSelect");

    if (programSelect) {
        programSelect.innerHTML = "";
        programSelect.appendChild(option("", "Program"));
        state.programs.forEach(program => {
            programSelect.appendChild(option(program.program_id, programLabel(program)));
        });
    }

    if (guardianSelect) {
        guardianSelect.innerHTML = "";
        guardianSelect.appendChild(option("", "Select Guardian"));
        state.guardians.forEach(guardian => {
            guardianSelect.appendChild(option(guardian.guardian_id, fullName(guardian.first_name, guardian.middle_name, guardian.last_name)));
        });
    }
}

function populateSubjectDropdown() {
    const select = byId("subPrerequisite");
    if (!select) return;

    select.innerHTML = "";
    select.appendChild(option("", "Prerequisite (optional)"));
    state.subjects.forEach(subject => {
        select.appendChild(option(subject.subject_code, `${subject.subject_code} - ${subject.title}`));
    });
}

function populateClassOfferingDropdowns() {
    const sectionSelect = byId("coSection");
    const subjectSelect = byId("coSubject");
    const scheduleSelect = byId("coSchedule");
    const instructorSelect = byId("coInstructor");

    if (sectionSelect) {
        sectionSelect.innerHTML = "";
        sectionSelect.appendChild(option("", "Section"));
        state.sections.forEach(section => {
            sectionSelect.appendChild(option(section.section_id, section.section_name));
        });
    }

    if (subjectSelect) {
        subjectSelect.innerHTML = "";
        subjectSelect.appendChild(option("", "Subject"));
        state.subjects.forEach(subject => {
            subjectSelect.appendChild(option(subject.subject_code, `${subject.subject_code} - ${subject.title}`));
        });
    }

    if (scheduleSelect) {
        scheduleSelect.innerHTML = "";
        scheduleSelect.appendChild(option("", "Schedule"));
        state.schedules.forEach(schedule => {
            scheduleSelect.appendChild(option(schedule.schedule_id, scheduleLabel(schedule)));
        });
    }

    if (instructorSelect) {
        instructorSelect.innerHTML = "";
        instructorSelect.appendChild(option("", "Instructor"));
        state.instructors.forEach(instructor => {
            instructorSelect.appendChild(option(instructor.instructor_id, instructor.name));
        });
    }
}

function populateRelationshipDropdowns() {
    const studentSelect = byId("relStudent");
    const guardianSelect = byId("relGuardian");

    if (studentSelect) {
        studentSelect.innerHTML = "";
        studentSelect.appendChild(option("", "Student"));
        state.students.forEach(student => {
            studentSelect.appendChild(option(student.student_id, studentLabel(student)));
        });
    }

    if (guardianSelect) {
        guardianSelect.innerHTML = "";
        guardianSelect.appendChild(option("", "Guardian"));
        state.guardians.forEach(guardian => {
            guardianSelect.appendChild(option(guardian.guardian_id, fullName(guardian.first_name, guardian.middle_name, guardian.last_name)));
        });
    }
}

function populateEnrollmentDropdowns() {
    const studentSelect = byId("enStudent");
    const classSelect = byId("enClass");

    if (studentSelect) {
        studentSelect.innerHTML = "";
        studentSelect.appendChild(option("", "Student"));
        state.students.forEach(student => {
            studentSelect.appendChild(option(student.student_id, studentLabel(student)));
        });
    }

    if (classSelect) {
        classSelect.innerHTML = "";
        classSelect.appendChild(option("", "Class Offering"));
        state.classOfferings.forEach(offering => {
            classSelect.appendChild(option(offering.class_offering_id, classOfferingLabel(offering)));
        });
    }
}

function populateProgramHistoryDropdowns() {
    const studentSelect = byId("phStudent");
    const programSelect = byId("phProgram");

    if (studentSelect) {
        studentSelect.innerHTML = "";
        studentSelect.appendChild(option("", "Student"));
        state.students.forEach(student => {
            studentSelect.appendChild(option(student.student_id, studentLabel(student)));
        });
    }

    if (programSelect) {
        programSelect.innerHTML = "";
        programSelect.appendChild(option("", "Program"));
        state.programs.forEach(program => {
            programSelect.appendChild(option(program.program_id, programLabel(program)));
        });
    }
}

function populateCurriculumDropdowns() {
    const programSelect = byId("curProgram");
    const subjectSelect = byId("curSubject");

    if (programSelect) {
        programSelect.innerHTML = "";
        programSelect.appendChild(option("", "Program"));
        state.programs.forEach(program => {
            programSelect.appendChild(option(program.program_id, programLabel(program)));
        });
    }

    if (subjectSelect) {
        subjectSelect.innerHTML = "";
        subjectSelect.appendChild(option("", "Subject"));
        state.subjects.forEach(subject => {
            subjectSelect.appendChild(option(subject.subject_code, `${subject.subject_code} - ${subject.title}`));
        });
    }
}

function populateClassScheduleDropdowns() {
    const classSelect = byId("csClass");
    const scheduleSelect = byId("csSchedule");

    if (classSelect) {
        classSelect.innerHTML = "";
        classSelect.appendChild(option("", "Class Offering"));
        state.classOfferings.forEach(offering => {
            classSelect.appendChild(option(offering.class_offering_id, classOfferingLabel(offering)));
        });
    }

    if (scheduleSelect) {
        scheduleSelect.innerHTML = "";
        scheduleSelect.appendChild(option("", "Schedule"));
        state.schedules.forEach(schedule => {
            scheduleSelect.appendChild(option(schedule.schedule_id, scheduleLabel(schedule)));
        });
    }
}

function setupLogin() {
    const loginButton = byId("loginButton");
    const loginForm = byId("loginForm");
    if (!loginButton && !loginForm) return;

    async function submitLogin(event) {
        if (event) event.preventDefault();

        try {
            const data = await apiFetch("/login", {
                method: "POST",
                body: JSON.stringify({
                    username: valueOf("username"),
                    password: valueOf("password")
                })
            });

            if (data.success) {
                window.location.href = "main.html";
            } else {
                alert("Invalid username or password.");
            }
        } catch (error) {
            alert(`Login failed: ${error.message}`);
        }
    }

    if (loginButton) loginButton.addEventListener("click", submitLogin);
    if (loginForm) loginForm.addEventListener("submit", submitLogin);
}

function setupNavigation() {
    document.querySelectorAll(".hasDropdown").forEach(button => {
        button.addEventListener("click", function () {
            this.parentElement.classList.toggle("open");
        });
    });

    document.querySelectorAll(".programButton, .subButton").forEach(button => {
        button.addEventListener("click", function () {
            document.querySelectorAll(".programButton, .subButton").forEach(item => item.classList.remove("active"));
            this.classList.add("active");

            document.querySelectorAll(".page").forEach(page => page.classList.remove("active"));
            const targetPage = byId(this.dataset.page);
            if (targetPage) {
                targetPage.classList.add("active");
            }
        });
    });
}

function setupSearches() {
    const configs = [
        ["searchStudentBar", () => renderFiltered("students", "searchStudentBar", renderStudents, ["lrn", "program_name", "major", row => fullName(row.first_name, row.middle_name, row.last_name), "guardian_name"])],
        ["searchGuardianBar", () => renderFiltered("guardians", "searchGuardianBar", renderGuardians, [row => fullName(row.first_name, row.middle_name, row.last_name), "contact_number"])],
        ["searchRelationshipBar", () => renderFiltered("relationships", "searchRelationshipBar", renderRelationships, ["student_name", "guardian_name", "relationship_type"])],
        ["searchEnrollmentBar", () => renderFiltered("enrollments", "searchEnrollmentBar", renderEnrollments, ["student_name", "subject_code", "subject_title", "section_name", "school_year", "sem"])],
        ["searchProgramHistoryBar", () => renderFiltered("programHistory", "searchProgramHistoryBar", renderProgramHistory, ["student_name", "program_name", "major", "school_year", "semester", "status"])],
        ["searchProgram", () => renderFiltered("programs", "searchProgram", renderPrograms, ["program_name", "major"])],
        ["searchSubjectBar", () => renderFiltered("subjects", "searchSubjectBar", renderSubjects, ["subject_code", "title", "prerequisite_code"])],
        ["searchCurriculumBar", () => renderFiltered("curriculums", "searchCurriculumBar", renderCurriculums, ["program_name", "major", "subject_code", "subject_title", "year_level", "semester"])],
        ["searchSectionBar", () => renderFiltered("sections", "searchSectionBar", renderSections, ["section_name"])],
        ["searchInstructorBar", () => renderFiltered("instructors", "searchInstructorBar", renderInstructors, ["name", "department"])],
        ["searchScheduleBar", () => renderFiltered("schedules", "searchScheduleBar", renderSchedules, ["day", "time_start", "time_end"])],
        ["searchClassOffering", () => renderFiltered("classOfferings", "searchClassOffering", renderClassOfferings, ["room", "section_name", "subject_code", "subject_title", "instructor_name", "school_year", "sem"])],
        ["searchClassScheduleBar", () => renderFiltered("classSchedules", "searchClassScheduleBar", renderClassSchedules, ["room", "section_name", "subject_code", "subject_title", "school_year", "sem", "day"])]
    ];

    configs.forEach(([inputId, handler]) => {
        const input = byId(inputId);
        if (input) input.addEventListener("input", handler);
    });
}

async function initializeMainPage() {
    if (!document.querySelector(".contentArea")) return;

    try {
        await Promise.all([
            loadStudents(),
            loadGuardians(),
            loadRelationships(),
            loadEnrollments(),
            loadProgramHistory(),
            loadPrograms(),
            loadSubjects(),
            loadCurriculums(),
            loadSections(),
            loadInstructors(),
            loadSchedules(),
            loadClassOfferings(),
            loadClassSchedules()
        ]);
    } catch (error) {
        handleLoadError(error);
    }
}

async function saveEntity(entityKey, basePath, payload, label) {
    const recordId = editing[entityKey];
    const method = recordId === null || recordId === undefined ? "POST" : "PUT";
    const path = recordId === null || recordId === undefined ? basePath : `${basePath}/${encodeURIComponent(recordId)}`;

    await apiFetch(path, {
        method,
        body: JSON.stringify(payload)
    });

    await initializeMainPage();
    closeEntityModal(entityKey);
    alert(`${label} ${method === "POST" ? "added" : "updated"}.`);
}

window.handleDelete = async function handleDelete(entityKey, recordId) {
    const config = {
        students: { path: `/students/${recordId}`, label: "student" },
        guardians: { path: `/guardians/${recordId}`, label: "guardian" },
        relationships: { path: `/relationships/${recordId}`, label: "relationship" },
        enrollments: { path: `/enrollments/${recordId}`, label: "enrollment" },
        programHistory: { path: `/program-history/${recordId}`, label: "program history record" },
        programs: { path: `/programs/${recordId}`, label: "program" },
        subjects: { path: `/subjects/${encodeURIComponent(recordId)}`, label: "subject" },
        curriculums: { path: `/curriculums/${recordId}`, label: "curriculum" },
        sections: { path: `/sections/${recordId}`, label: "section" },
        instructors: { path: `/instructors/${recordId}`, label: "instructor" },
        schedules: { path: `/schedules/${recordId}`, label: "schedule" },
        classOfferings: { path: `/class-offerings/${recordId}`, label: "class offering" },
        classSchedules: { path: `/class-schedules/${recordId}`, label: "class schedule" }
    }[entityKey];

    if (!config) return;
    if (!confirm(`Delete this ${config.label}?`)) return;

    try {
        await apiFetch(config.path, { method: "DELETE" });
        await initializeMainPage();
        alert(`${config.label.charAt(0).toUpperCase()}${config.label.slice(1)} deleted.`);
    } catch (error) {
        alert(`Failed to delete ${config.label}: ${error.message}`);
    }
};

async function editStudent(studentId) {
    await Promise.all([loadPrograms(), loadGuardians()]);
    const student = getRecord("students", studentId);
    if (!student) return;

    populateStudentDropdowns();
    const modal = setModalMode("students", studentId);
    byId("lrn").value = student.lrn || "";
    byId("firstName").value = student.first_name || "";
    byId("middleName").value = student.middle_name || "";
    byId("lastName").value = student.last_name || "";
    byId("birthdate").value = student.birthdate || "";
    byId("gender").value = student.gender || "";
    byId("address").value = student.address || "";
    byId("contact").value = student.contact_no || "";
    byId("program").value = student.program_id || "";
    byId("studentGuardianSelect").value = student.guardian_id || "";
    byId("studentRelationshipType").value = student.relationship_type || "";
    showModal(modal);
}

async function editGuardian(guardianId) {
    const guardian = getRecord("guardians", guardianId);
    if (!guardian) return;

    const modal = setModalMode("guardians", guardianId);
    byId("gFirstName").value = guardian.first_name || "";
    byId("gMiddleName").value = guardian.middle_name || "";
    byId("gLastName").value = guardian.last_name || "";
    byId("gContact").value = guardian.contact_number || "";
    showModal(modal);
}

async function editRelationship(relationshipId) {
    await Promise.all([loadStudents(), loadGuardians()]);
    const relationship = getRecord("relationships", relationshipId);
    if (!relationship) return;

    populateRelationshipDropdowns();
    const modal = setModalMode("relationships", relationshipId);
    byId("relStudent").value = relationship.student_id || "";
    byId("relGuardian").value = relationship.guardian_id || "";
    byId("relType").value = relationship.relationship_type || "";
    showModal(modal);
}

async function editEnrollment(enrollmentId) {
    await Promise.all([loadStudents(), loadClassOfferings()]);
    const enrollment = getRecord("enrollments", enrollmentId);
    if (!enrollment) return;

    populateEnrollmentDropdowns();
    const modal = setModalMode("enrollments", enrollmentId);
    byId("enStudent").value = enrollment.student_id || "";
    byId("enClass").value = enrollment.class_id || "";
    showModal(modal);
}

async function editProgramHistory(historyId) {
    await Promise.all([loadStudents(), loadPrograms()]);
    const history = getRecord("programHistory", historyId);
    if (!history) return;

    populateProgramHistoryDropdowns();
    const modal = setModalMode("programHistory", historyId);
    byId("phStudent").value = history.student_id || "";
    byId("phProgram").value = history.program_id || "";
    byId("phSchoolYear").value = history.school_year || "";
    byId("phSemester").value = history.semester || "";
    byId("phStatus").value = history.status || "";
    showModal(modal);
}

async function editProgram(programId) {
    const program = getRecord("programs", programId);
    if (!program) return;

    const modal = setModalMode("programs", programId);
    byId("progName").value = program.program_name || "";
    byId("progMajor").value = program.major || "";
    showModal(modal);
}

async function editSubject(subjectCode) {
    const subject = getRecord("subjects", subjectCode);
    if (!subject) return;

    await loadSubjects();
    populateSubjectDropdown();
    const modal = setModalMode("subjects", subjectCode);
    byId("subCode").value = subject.subject_code || "";
    byId("subTitle").value = subject.title || "";
    byId("subUnits").value = subject.units || "";
    byId("subPrerequisite").value = subject.prerequisite_code || "";
    showModal(modal);
}

async function editCurriculum(curriculumId) {
    await Promise.all([loadPrograms(), loadSubjects()]);
    const curriculum = getRecord("curriculums", curriculumId);
    if (!curriculum) return;

    populateCurriculumDropdowns();
    const modal = setModalMode("curriculums", curriculumId);
    byId("curProgram").value = curriculum.program_id || "";
    byId("curSubject").value = curriculum.subject_code || "";
    byId("curYearLevel").value = curriculum.year_level || "";
    byId("curSemester").value = curriculum.semester || "";
    showModal(modal);
}

async function editSection(sectionId) {
    const section = getRecord("sections", sectionId);
    if (!section) return;

    const modal = setModalMode("sections", sectionId);
    byId("sectionName").value = section.section_name || "";
    showModal(modal);
}

async function editInstructor(instructorId) {
    const instructor = getRecord("instructors", instructorId);
    if (!instructor) return;

    const modal = setModalMode("instructors", instructorId);
    byId("insName").value = instructor.name || "";
    byId("insDepartment").value = instructor.department || "";
    byId("insContact").value = instructor.contact_number || "";
    showModal(modal);
}

async function editSchedule(scheduleId) {
    const schedule = getRecord("schedules", scheduleId);
    if (!schedule) return;

    const modal = setModalMode("schedules", scheduleId);
    byId("schDay").value = schedule.day || "";
    byId("schStart").value = String(schedule.time_start || "").slice(0, 5);
    byId("schEnd").value = String(schedule.time_end || "").slice(0, 5);
    showModal(modal);
}

async function editClassOffering(classId) {
    await Promise.all([loadSections(), loadSubjects(), loadSchedules(), loadInstructors()]);
    const offering = getRecord("classOfferings", classId);
    if (!offering) return;

    populateClassOfferingDropdowns();
    const modal = setModalMode("classOfferings", classId);
    byId("coRoom").value = offering.room || "";
    byId("coSection").value = offering.section_id || "";
    byId("coSubject").value = offering.subject_code || "";
    byId("coSchedule").value = offering.schedule_id || "";
    byId("coInstructor").value = offering.instructor_id || "";
    byId("coSchoolYear").value = offering.school_year || "";
    byId("coSem").value = offering.sem || "";
    showModal(modal);
}

async function editClassSchedule(classScheduleId) {
    await Promise.all([loadClassOfferings(), loadSchedules()]);
    const classSchedule = getRecord("classSchedules", classScheduleId);
    if (!classSchedule) return;

    populateClassScheduleDropdowns();
    const modal = setModalMode("classSchedules", classScheduleId);
    byId("csClass").value = classSchedule.class_id || "";
    byId("csSchedule").value = classSchedule.schedule_id || "";
    showModal(modal);
}

window.handleEdit = async function handleEdit(entityKey, recordId) {
    const handlers = {
        students: editStudent,
        guardians: editGuardian,
        relationships: editRelationship,
        enrollments: editEnrollment,
        programHistory: editProgramHistory,
        programs: editProgram,
        subjects: editSubject,
        curriculums: editCurriculum,
        sections: editSection,
        instructors: editInstructor,
        schedules: editSchedule,
        classOfferings: editClassOffering,
        classSchedules: editClassSchedule
    };

    const handler = handlers[entityKey];
    if (!handler) return;

    try {
        await handler(recordId);
    } catch (error) {
        handleLoadError(error);
    }
};

function setupForms() {
    const addStudentButton = byId("addStudentBtn");
    if (addStudentButton) {
        addStudentButton.onclick = async () => {
            try {
                await Promise.all([loadPrograms(), loadGuardians()]);
                populateStudentDropdowns();
                const modal = setModalMode("students", null);
                resetModal(modal);
                showModal(modal);
            } catch (error) {
                handleLoadError(error);
            }
        };
    }

    const saveStudentButton = byId("saveStudent");
    if (saveStudentButton) {
        saveStudentButton.onclick = async () => {
            const payload = {
                LRN: valueOf("lrn"),
                FirstName: valueOf("firstName"),
                MiddleName: valueOf("middleName"),
                LastName: valueOf("lastName"),
                Birthdate: valueOf("birthdate"),
                Gender: valueOf("gender"),
                Address: valueOf("address"),
                Contact: valueOf("contact"),
                ProgramID: valueOf("program"),
                GuardianID: valueOf("studentGuardianSelect"),
                RelationshipType: valueOf("studentRelationshipType")
            };

            if (!payload.LRN || !payload.FirstName || !payload.LastName) {
                alert("Please fill LRN, first name, and last name.");
                return;
            }

            try {
                await saveEntity("students", "/students", payload, "Student");
            } catch (error) {
                alert(`Failed to save student: ${error.message}`);
            }
        };
    }

    const addGuardianButton = document.querySelector("#guardians .addButton");
    if (addGuardianButton) {
        addGuardianButton.onclick = () => {
            const modal = setModalMode("guardians", null);
            resetModal(modal);
            showModal(modal);
        };
    }

    const saveGuardianButton = byId("saveGuardian");
    if (saveGuardianButton) {
        saveGuardianButton.onclick = async () => {
            try {
                await saveEntity("guardians", "/guardians", {
                    FirstName: valueOf("gFirstName"),
                    MiddleName: valueOf("gMiddleName"),
                    LastName: valueOf("gLastName"),
                    ContactNumber: valueOf("gContact")
                }, "Guardian");
            } catch (error) {
                alert(`Failed to save guardian: ${error.message}`);
            }
        };
    }

    const addRelationshipButton = document.querySelector("#relationships .addButton");
    if (addRelationshipButton) {
        addRelationshipButton.onclick = async () => {
            try {
                await Promise.all([loadStudents(), loadGuardians()]);
                populateRelationshipDropdowns();
                const modal = setModalMode("relationships", null);
                resetModal(modal);
                showModal(modal);
            } catch (error) {
                handleLoadError(error);
            }
        };
    }

    const saveRelationshipButton = byId("saveRelationship");
    if (saveRelationshipButton) {
        saveRelationshipButton.onclick = async () => {
            try {
                await saveEntity("relationships", "/relationships", {
                    StudentID: valueOf("relStudent"),
                    GuardianID: valueOf("relGuardian"),
                    RelationshipType: valueOf("relType")
                }, "Relationship");
            } catch (error) {
                alert(`Failed to save relationship: ${error.message}`);
            }
        };
    }

    const addEnrollmentButton = document.querySelector("#enrollments .addButton");
    if (addEnrollmentButton) {
        addEnrollmentButton.onclick = async () => {
            try {
                await Promise.all([loadStudents(), loadClassOfferings()]);
                populateEnrollmentDropdowns();
                const modal = setModalMode("enrollments", null);
                resetModal(modal);
                showModal(modal);
            } catch (error) {
                handleLoadError(error);
            }
        };
    }

    const saveEnrollmentButton = byId("saveEnrollment");
    if (saveEnrollmentButton) {
        saveEnrollmentButton.onclick = async () => {
            try {
                await saveEntity("enrollments", "/enrollments", {
                    StudentID: valueOf("enStudent"),
                    ClassID: valueOf("enClass")
                }, "Enrollment");
            } catch (error) {
                alert(`Failed to save enrollment: ${error.message}`);
            }
        };
    }

    const addProgramHistoryButton = document.querySelector("#programHistory .addButton");
    if (addProgramHistoryButton) {
        addProgramHistoryButton.onclick = async () => {
            try {
                await Promise.all([loadStudents(), loadPrograms()]);
                populateProgramHistoryDropdowns();
                const modal = setModalMode("programHistory", null);
                resetModal(modal);
                showModal(modal);
            } catch (error) {
                handleLoadError(error);
            }
        };
    }

    const saveProgramHistoryButton = byId("saveProgramHistory");
    if (saveProgramHistoryButton) {
        saveProgramHistoryButton.onclick = async () => {
            try {
                await saveEntity("programHistory", "/program-history", {
                    StudentID: valueOf("phStudent"),
                    ProgramID: valueOf("phProgram"),
                    SchoolYear: valueOf("phSchoolYear"),
                    Semester: valueOf("phSemester"),
                    Status: valueOf("phStatus")
                }, "Program history");
            } catch (error) {
                alert(`Failed to save program history: ${error.message}`);
            }
        };
    }

    const addProgramButton = document.querySelector("#programs .addButton");
    if (addProgramButton) {
        addProgramButton.onclick = () => {
            const modal = setModalMode("programs", null);
            resetModal(modal);
            showModal(modal);
        };
    }

    const saveProgramButton = byId("saveProgram");
    if (saveProgramButton) {
        saveProgramButton.onclick = async () => {
            try {
                await saveEntity("programs", "/programs", {
                    ProgramName: valueOf("progName"),
                    Major: valueOf("progMajor")
                }, "Program");
            } catch (error) {
                alert(`Failed to save program: ${error.message}`);
            }
        };
    }

    const addSubjectButton = byId("addSubjectBtn");
    if (addSubjectButton) {
        addSubjectButton.onclick = async () => {
            try {
                await loadSubjects();
                populateSubjectDropdown();
                const modal = setModalMode("subjects", null);
                resetModal(modal);
                showModal(modal);
            } catch (error) {
                handleLoadError(error);
            }
        };
    }

    const saveSubjectButton = byId("saveSubject");
    if (saveSubjectButton) {
        saveSubjectButton.onclick = async () => {
            try {
                await saveEntity("subjects", "/subjects", {
                    SubjectCode: valueOf("subCode"),
                    Title: valueOf("subTitle"),
                    Units: valueOf("subUnits"),
                    Prerequisite: valueOf("subPrerequisite")
                }, "Subject");
            } catch (error) {
                alert(`Failed to save subject: ${error.message}`);
            }
        };
    }

    const addCurriculumButton = document.querySelector("#curriculums .addButton");
    if (addCurriculumButton) {
        addCurriculumButton.onclick = async () => {
            try {
                await Promise.all([loadPrograms(), loadSubjects()]);
                populateCurriculumDropdowns();
                const modal = setModalMode("curriculums", null);
                resetModal(modal);
                showModal(modal);
            } catch (error) {
                handleLoadError(error);
            }
        };
    }

    const saveCurriculumButton = byId("saveCurriculum");
    if (saveCurriculumButton) {
        saveCurriculumButton.onclick = async () => {
            try {
                await saveEntity("curriculums", "/curriculums", {
                    ProgramID: valueOf("curProgram"),
                    SubjectCode: valueOf("curSubject"),
                    YearLevel: valueOf("curYearLevel"),
                    Semester: valueOf("curSemester")
                }, "Curriculum");
            } catch (error) {
                alert(`Failed to save curriculum: ${error.message}`);
            }
        };
    }

    const addSectionButton = document.querySelector("#sections .addButton");
    if (addSectionButton) {
        addSectionButton.onclick = () => {
            const modal = setModalMode("sections", null);
            resetModal(modal);
            showModal(modal);
        };
    }

    const saveSectionButton = byId("saveSection");
    if (saveSectionButton) {
        saveSectionButton.onclick = async () => {
            try {
                await saveEntity("sections", "/sections", {
                    SectionName: valueOf("sectionName")
                }, "Section");
            } catch (error) {
                alert(`Failed to save section: ${error.message}`);
            }
        };
    }

    const addInstructorButton = document.querySelector("#instructors .addButton");
    if (addInstructorButton) {
        addInstructorButton.onclick = () => {
            const modal = setModalMode("instructors", null);
            resetModal(modal);
            showModal(modal);
        };
    }

    const saveInstructorButton = byId("saveInstructor");
    if (saveInstructorButton) {
        saveInstructorButton.onclick = async () => {
            try {
                await saveEntity("instructors", "/instructors", {
                    Name: valueOf("insName"),
                    Department: valueOf("insDepartment"),
                    ContactNumber: valueOf("insContact")
                }, "Instructor");
            } catch (error) {
                alert(`Failed to save instructor: ${error.message}`);
            }
        };
    }

    const addScheduleButton = document.querySelector("#schedules .addButton");
    if (addScheduleButton) {
        addScheduleButton.onclick = () => {
            const modal = setModalMode("schedules", null);
            resetModal(modal);
            showModal(modal);
        };
    }

    const saveScheduleButton = byId("saveSchedule");
    if (saveScheduleButton) {
        saveScheduleButton.onclick = async () => {
            try {
                await saveEntity("schedules", "/schedules", {
                    Day: valueOf("schDay"),
                    TimeStart: valueOf("schStart"),
                    TimeEnd: valueOf("schEnd")
                }, "Schedule");
            } catch (error) {
                alert(`Failed to save schedule: ${error.message}`);
            }
        };
    }

    const addClassOfferingButton = document.querySelector("#classOfferings .addButton");
    if (addClassOfferingButton) {
        addClassOfferingButton.onclick = async () => {
            try {
                await Promise.all([loadSections(), loadSubjects(), loadSchedules(), loadInstructors()]);
                populateClassOfferingDropdowns();
                const modal = setModalMode("classOfferings", null);
                resetModal(modal);
                showModal(modal);
            } catch (error) {
                handleLoadError(error);
            }
        };
    }

    const saveClassOfferingButton = byId("saveClassOffering");
    if (saveClassOfferingButton) {
        saveClassOfferingButton.onclick = async () => {
            try {
                await saveEntity("classOfferings", "/class-offerings", {
                    Room: valueOf("coRoom"),
                    SectionID: valueOf("coSection"),
                    SubjectCode: valueOf("coSubject"),
                    ScheduleID: valueOf("coSchedule"),
                    InstructorID: valueOf("coInstructor"),
                    SchoolYear: valueOf("coSchoolYear"),
                    Sem: valueOf("coSem")
                }, "Class offering");
            } catch (error) {
                alert(`Failed to save class offering: ${error.message}`);
            }
        };
    }

    const addClassScheduleButton = document.querySelector("#classSchedules .addButton");
    if (addClassScheduleButton) {
        addClassScheduleButton.onclick = async () => {
            try {
                await Promise.all([loadClassOfferings(), loadSchedules()]);
                populateClassScheduleDropdowns();
                const modal = setModalMode("classSchedules", null);
                resetModal(modal);
                showModal(modal);
            } catch (error) {
                handleLoadError(error);
            }
        };
    }

    const saveClassScheduleButton = byId("saveClassSchedule");
    if (saveClassScheduleButton) {
        saveClassScheduleButton.onclick = async () => {
            try {
                await saveEntity("classSchedules", "/class-schedules", {
                    ClassID: valueOf("csClass"),
                    ScheduleID: valueOf("csSchedule")
                }, "Class schedule");
            } catch (error) {
                alert(`Failed to save class schedule: ${error.message}`);
            }
        };
    }

    Object.entries(modalConfig).forEach(([entityKey, config]) => {
        const button = byId(config.closeButtonId);
        if (button) {
            button.onclick = () => closeEntityModal(entityKey);
        }
    });
}

document.addEventListener("DOMContentLoaded", () => {
    setupLogin();
    setupNavigation();
    setupSearches();
    setupForms();
    initializeMainPage();
});
