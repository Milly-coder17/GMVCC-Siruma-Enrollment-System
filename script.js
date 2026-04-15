let editingStudentId = null;
const buttons = document.querySelectorAll(".navBtn");
const pages = document.querySelectorAll(".page");

buttons.forEach(button => {
    button.addEventListener("click", () => {
        buttons.forEach(btn => btn.classList.remove("active"));
        button.classList.add("active");
        pages.forEach(page => page.classList.remove("active"));
        const targetPage = document.getElementById(button.dataset.page);
        targetPage.classList.add("active");
    });
});

const loginForm = document.getElementById("loginForm");
if (loginForm) {
    loginForm.addEventListener("submit", async function(e) {
        e.preventDefault();

        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        try {
            const res = await fetch("http://127.0.0.1:5000/api/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ username, password })
            });

            const data = await res.json();
            const searchValue = document.getElementById("searchBar") 
            ? document.getElementById("searchBar").value.toLowerCase() 
            : "";

            if (data.success) {
                localStorage.setItem("user", username);
                window.location.href = "main.html";
            } else {
                alert("Invalid username or password");
            }

        } catch (error) {
            console.error(error);
            alert("Error connecting to server");
        }
    });
}

const studentForm = document.getElementById("studentForm");
const openStudentBtn = document.getElementById("addMainBtn");
const closeStudentBtn = document.getElementById("closeBtn"); 
const clearStudentBtn = document.getElementById("clearBtn");
const saveStudentBtn = document.getElementById("addStudentBtn");

if (openStudentBtn) {
    openStudentBtn.addEventListener("click", () => {
        studentForm.style.display = "flex";
    });
}

if (closeStudentBtn) {
    closeStudentBtn.addEventListener("click", () => {
        studentForm.style.display = "none";
    });
}

if (clearStudentBtn) {
    clearStudentBtn.addEventListener("click", () => {
        document.querySelectorAll("#studentForm input").forEach(input => input.value = "");
        document.getElementById("gender").value = "";
        document.getElementById("program").value = "";
    });
}

if (saveStudentBtn) {
    saveStudentBtn.addEventListener("click", async () => {
        const studentData = {
            lrn: document.getElementById("lrn").value,
            fname: document.getElementById("fname").value,
            mname: document.getElementById("mname").value,
            lname: document.getElementById("lname").value,
            program: document.getElementById("program").value,
            bday: document.getElementById("birthdate").value, 
            gender: document.getElementById("gender").value,
            address: document.getElementById("address").value,
            contact: document.getElementById("contact").value 
        };

        if (!studentData.lrn || !studentData.fname || !studentData.lname) {
            alert("Please fill out required fields (LRN, First Name, Last Name)");
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/api/students', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(studentData)
            });

            if (response.ok) {
                alert("Student successfully saved to database!");
                
                studentForm.style.display = "none";
                document.querySelectorAll("#studentForm input").forEach(input => input.value = "");
                
                loadStudents(); 
            } else {
                const error = await response.json();
                alert("Error: " + (error.message || "Failed to save student."));
            }
        } catch (error) {
            console.error("Connection Error:", error);
            alert("Could not connect to the server. Is app.py running?");
        }
    });
}

const addSubjectBtn = document.getElementById("addSubjectBtn");
const subjectForm = document.getElementById("subjectForm");
const saveSubjectBtn = document.getElementById("saveSubjectBtn");

if (addSubjectBtn && subjectForm) {
    addSubjectBtn.addEventListener("click", () => {
        subjectForm.style.display = "flex";
    });
}
if (saveSubjectBtn) {
    saveSubjectBtn.addEventListener("click", async () => {
        const subjectData = {
            code: document.getElementById("subjectCode").value,
            title: document.getElementById("subjectTitle").value,
            units: document.getElementById("subjectUnits").value
        };

        if (!subjectData.code || !subjectData.title || !subjectData.units) {
            alert("Please fill out all fields");
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/api/subjects', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(subjectData)
            });

            if (response.ok) {
                alert("Subject saved successfully!");
                subjectForm.style.display = "none";
                loadSubjects();
            } else {
                alert("Error: Could not save subject. Check if the code is a duplicate.");
            }
        } catch (error) {
            alert("Backend Error: Is app.py running?");
        }
    });
}

const addClassBtn = document.getElementById("addClassBtn");
const classForm = document.getElementById("classForm");
const classTableBody = document.getElementById("classTableBody");
const closeClassBtn = document.getElementById("closeClassBtn");
const clearClassBtn = document.getElementById("clearClassBtn");
const saveClassBtn = document.getElementById("saveClassBtn");

const classSubject = document.getElementById("classSubject");
const classSection = document.getElementById("classSection");
const classInstructor = document.getElementById("classInstructor");

if (addClassBtn && classForm) {
    addClassBtn.addEventListener("click", () => {
    loadClassDropdowns();
    classForm.style.display = "flex";
});
}

if (closeClassBtn && classForm) {
    closeClassBtn.addEventListener("click", () => {
        classForm.style.display = "none";
    });
}

if (clearClassBtn) {
    clearClassBtn.addEventListener("click", () => {

        if (classSubject) classSubject.value = "";
        if (classSection) classSection.value = "";
        if (classInstructor) classInstructor.value = "";

        const room = document.getElementById("classRoom");
        const semester = document.getElementById("classSemester");
        const schoolYear = document.getElementById("classSchoolYear");
        const schedule = document.getElementById("classSchedule");

        if (room) room.value = "";
        if (semester) semester.value = "";
        if (schoolYear) schoolYear.value = "";
        if (schedule) schedule.value = "";
    });
}

if (saveClassBtn) {
    saveClassBtn.addEventListener("click", async () => {
        const classData = {
            subject: document.getElementById("classSubject").value,
            section: document.getElementById("classSection").value,
            room: document.getElementById("classRoom").value,
            semester: document.getElementById("classSemester").value,
            school_year: document.getElementById("classSchoolYear").value,
            schedule: document.getElementById("classSchedule").value,
            instructor: document.getElementById("classInstructor").value
        };

        if (!classData.subject || !classData.section || !classData.schedule || !classData.instructor) {
            alert("Please complete all selections!");
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/api/classes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(classData)
            });

            if (response.ok) {
                alert("Class Offering successfully added!");
                location.reload();
            } else {
                alert("Failed to save class. Check terminal for errors.");
            }
        } catch (error) {
            alert("Error: Backend is not responding. Is app.py running?");
        }
    });
}

const addProgramBtn = document.getElementById("addProgramBtn");
const programForm = document.getElementById("programForm");
const closeBtn2 = document.getElementById("closeBtn2");
const saveProgramBtn = document.getElementById("saveProgramBtn");

if (addProgramBtn && programForm) {
    addProgramBtn.addEventListener("click", () => {
        programForm.style.display = "flex";
    });
}

if (closeBtn2) {
    closeBtn2.addEventListener("click", () => {
        programForm.style.display = "none";
    });
}

if (saveProgramBtn) {
    saveProgramBtn.addEventListener("click", async () => {
        const programData = {
            name: document.getElementById("programName").value,
            desc: document.getElementById("programDesc").value,
            type: document.getElementById("programType").value
        };

        if (!programData.name || !programData.desc) {
            alert("Please fill out the Program Name and Description.");
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/api/programs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(programData)
            });

            if (response.ok) {
                alert("Program saved successfully!");
                programForm.style.display = "none";
                
                document.getElementById("programName").value = "";
                document.getElementById("programDesc").value = "";
                
                const programGrid = document.getElementById("programGrid");
                if (programGrid) programGrid.innerHTML = "";
                loadPrograms(); 
            } else {
                alert("Failed to save program.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Connection error. Is app.py running?");
        }
    });
}

const addInstructorBtn = document.getElementById("addInstructorBtn");
const instructorForm = document.getElementById("instructorForm");
const closeInstructorBtn = document.getElementById("closeInstructorBtn");
const clearInstructorBtn = document.getElementById("clearInstructorBtn");
const saveInstructorBtn = document.getElementById("saveInstructorBtn");
const instructorTableBody = document.getElementById("instructorTableBody");

if (addInstructorBtn && instructorForm) {
    addInstructorBtn.addEventListener("click", () => {
        instructorForm.style.display = "flex";
    });
}

if (closeInstructorBtn) {
    closeInstructorBtn.addEventListener("click", () => {
        instructorForm.style.display = "none";
    });
}

if (clearInstructorBtn) {
    clearInstructorBtn.addEventListener("click", () => {

        document.getElementById("ifname").value = "";
        document.getElementById("imname").value = "";
        document.getElementById("ilname").value = "";
        document.getElementById("idepartment").value = "";
        document.getElementById("icontact").value = "";

    });
}

if (saveInstructorBtn) {
    saveInstructorBtn.addEventListener("click", async () => {
    
        const instructorData = {
            fname: document.getElementById("ifname").value,
            mname: document.getElementById("imname").value,
            lname: document.getElementById("ilname").value,
            dept: document.getElementById("idepartment").value,
            contact: document.getElementById("icontact").value
        };

        if (!instructorData.fname || !instructorData.lname || !instructorData.dept) {
            alert("Please fill out required fields (First Name, Last Name, and Department)");
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:5000/api/instructors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(instructorData)
            });

            if (response.ok) {
                alert("Instructor added successfully!");
                
                instructorForm.style.display = "none";

                document.getElementById("ifname").value = "";
                document.getElementById("imname").value = "";
                document.getElementById("ilname").value = "";
                document.getElementById("idepartment").value = "";
                document.getElementById("icontact").value = "";

                loadInstructors(); 
            } else {
                alert("Failed to save instructor to the database.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("Connection error. Is app.py running?");
        }
    });
}
function loadClassDropdowns() {

    const classSubject = document.getElementById("classSubject");
    const classInstructor = document.getElementById("classInstructor");

    if (!classSubject || !classInstructor) return;

    classSubject.innerHTML = `<option value="">Select Subject</option>`;
    classInstructor.innerHTML = `<option value="">Select Instructor</option>`;

    document.querySelectorAll("#subjectTableBody tr").forEach(row => {

        const code = row.children[1].textContent;
        const title = row.children[2].textContent;

        const option = document.createElement("option");
        option.value = code;
        option.textContent = code + " - " + title;

        classSubject.appendChild(option);
    });

    document.querySelectorAll("#instructorTableBody tr").forEach(row => {

        const name = row.children[1].textContent;

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;

        classInstructor.appendChild(option);
    });
}

async function loadClasses() {
    const tableBody = document.getElementById("classTableBody");
    if (!tableBody) return;

    try {
        const response = await fetch('http://127.0.0.1:5000/api/classes');
        const classes = await response.json();

        tableBody.innerHTML = "";
        const searchValue = searchBar 
    ? searchBar.value.toLowerCase() 
    : "";

        classes
.filter(item => 
    item.subject_name.toLowerCase().includes(searchValue) ||
    item.section.toLowerCase().includes(searchValue) ||
    item.instructor_name.toLowerCase().includes(searchValue)
)
.forEach((item, index) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${item.subject_name}</td>
                <td>${item.section}</td>
                <td>${item.room}</td>
                <td>${item.semester}</td>
                <td>${item.school_year}</td>
                <td>${item.schedule}</td>
                <td>${item.instructor_name}</td>
                <td>
                    <button onclick="editClass(${item.id}, '${item.section}', '${item.room}', '${item.schedule}')">Edit</button>
                    <button onclick="deleteClass(${item.id})">Delete</button>
                </td>
            `;
            tableBody.appendChild(row);
        });
    } catch (err) {
        console.error("Failed to load table:", err);
    }
}

async function loadStudents() {
    const table = document.getElementById("studentTable");
    if (!table) return;

    try {
        const res = await fetch("http://127.0.0.1:5000/api/students");
        const data = await res.json();
        const searchValue = document.getElementById("searchBar") 
    ? document.getElementById("searchBar").value.toLowerCase() 
    : "";
        
        table.innerHTML = "";

        data
.filter(s => 
    s.full_name.toLowerCase().includes(searchValue) ||
    s.lrn.toLowerCase().includes(searchValue)
)
.forEach((s, i) => {
            const dateObj = new Date(s.birthdate);

            const formattedDate = dateObj.toLocaleDateString('en-US', {
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            });

            table.innerHTML += `
<tr>
    <td>${i + 1}</td>
    <td>${s.lrn}</td>
    <td>${s.program}</td>
    <td>${s.full_name}</td>
    <td>${formattedDate}</td> 
    <td>${s.gender}</td>
    <td>${s.address}</td>
    <td>${s.contact_number}</td>
    <td>
        <button onclick='editStudent(${JSON.stringify(s)})'>Edit</button>
        <button onclick="deleteStudent(${s.id})">Delete</button>
    </td>
</tr>
`;
        });
    } catch (err) {
        console.error("Failed to load students:", err);
    }
}

async function loadInstructors() {
    const table = document.getElementById("instructorTableBody");
    if (!table) return;

    try {
        const res = await fetch("http://127.0.0.1:5000/api/instructors");
        const data = await res.json();

        table.innerHTML = "";

        data.forEach((i, index) => {
            table.innerHTML += `
                <tr>
                <td>${index + 1}</td>
                <td>${i.full_name}</td>
                <td>${i.department}</td>
                <td>${i.contact}</td>
                <td>
                <button onclick='editInstructor(${JSON.stringify(i)})'>Edit</button>
                <button onclick="deleteInstructor(${i.id})">Delete</button>
            </td>
        </tr>
    `;
        });
    } catch (err) {
        console.error("Failed to load instructors:", err);
    }
}
async function loadPrograms() {
    const programGrid = document.getElementById("programGrid");
    if (!programGrid) return;

    programGrid.innerHTML = ""

    try {
        const response = await fetch('http://127.0.0.1:5000/api/programs');
        const programs = await response.json();


        const searchValue = searchBar 
        ? searchBar.value.toLowerCase() 
        : "";

        programs
        .filter(prog => 
            prog.name.toLowerCase().includes(searchValue) ||
            prog.description.toLowerCase().includes(searchValue)
        )
        .forEach(prog => {
            const card = document.createElement("div");
            card.classList.add("program-card");
            if(prog.type === 'Department') card.classList.add("main-program");

            card.innerHTML = `
    <div class="program-tag">${prog.type}</div>
    <h3>${prog.name}</h3>
    <p>${prog.description}</p>
    <div class="program-footer">
        <span>Total Students: 0</span>
        <button onclick="deleteProgram(${prog.id})">Delete</button>
    </div>
`;
            programGrid.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load programs:", err);
    }
}
async function loadSubjects() {
    const table = document.getElementById("subjectTableBody");
    if (!table) return;

    try {
        const res = await fetch("http://127.0.0.1:5000/api/subjects"); // ✅ MISSING LINE
        const data = await res.json();

        const searchValue = searchBar 
            ? searchBar.value.toLowerCase() 
            : "";

        table.innerHTML = "";

        data
        .filter(s => 
            s.title.toLowerCase().includes(searchValue) ||
            s.code.toLowerCase().includes(searchValue)
        )
        .forEach((s, i) => {
            table.innerHTML += `
<tr>
    <td>${i + 1}</td>
    <td>${s.code}</td>
    <td>${s.title}</td>
    <td>-</td> 
    <td style="text-align:center;">${s.units}</td>
    <td style="text-align:center;">
        <button onclick='editSubject(${JSON.stringify(s)})'>Edit</button>
        <button onclick="deleteSubject(${s.id})">Delete</button>
    </td>
</tr>
`;
        });

    } catch (err) {
        console.error("Failed to load subjects:", err);
    }
}
async function deleteStudent(id) {
    if (!confirm("Delete this student?")) return;

    try {
        await fetch(`http://127.0.0.1:5000/api/students/${id}`, {
            method: "DELETE"
        });

        alert("Student deleted!");
        loadStudents();

    } catch (error) {
        alert("Delete failed. Is backend running?");
    }
}
const searchBar = document.getElementById("searchBar");

searchBar.addEventListener("input", () => {
    loadStudents();
    loadSubjects();
});
async function editStudent(student) {
    const id = student.id; // ✅ FIX

    const newName = prompt("Enter new name:", student.full_name);
    const newProgram = prompt("Enter new program:", student.program);

    if (!newName || !newProgram) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/api/students/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                full_name: newName,
                program: newProgram
            })
        });

        if (res.ok) {
            alert("Student updated!");
            loadStudents();
        } else {
            alert("Update failed");
        }

    } catch (err) {
        alert("Server error");
    }
}
async function deleteProgram(id) {
    if (!confirm("Delete this program?")) return;

    try {
        await fetch(`http://127.0.0.1:5000/api/programs/${id}`, {
            method: "DELETE"
        });

        alert("Program deleted!");
        document.getElementById("programGrid").innerHTML = "";
        loadPrograms();

    } catch (err) {
        alert("Delete failed");
    }
}
async function deleteSubject(id) {
    if (!confirm("Delete this subject?")) return;

    try {
        await fetch(`http://127.0.0.1:5000/api/subjects/${id}`, {
            method: "DELETE"
        });

        alert("Subject deleted!");
        loadSubjects();

    } catch (err) {
        alert("Delete failed");
    }
}
async function editSubject(subject) {
    const id = subject.id;

    const newCode = prompt("Subject Code:", subject.code);
    const newTitle = prompt("Subject Title:", subject.title);
    const newUnits = prompt("Units:", subject.units);

    if (!newCode || !newTitle || !newUnits) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/api/subjects/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                code: newCode,
                title: newTitle,
                units: newUnits
            })
        });

        if (res.ok) {
            alert("Updated!");
            loadSubjects();
        }

    } catch {
        alert("Error updating");
    }
}
async function deleteInstructor(id) {
    if (!confirm("Delete this instructor?")) return;

    try {
        await fetch(`http://127.0.0.1:5000/api/instructors/${id}`, {
            method: "DELETE"
        });

        alert("Instructor deleted!");
        loadInstructors();

    } catch {
        alert("Delete failed");
    }
}
async function editInstructor(instructor) {
    const id = instructor.id;

    const newName = prompt("Full Name:", instructor.full_name);
    const newDept = prompt("Department:", instructor.department);
    const newContact = prompt("Contact:", instructor.contact);

    if (!newName || !newDept) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/api/instructors/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                full_name: newName,
                department: newDept,
                contact: newContact
            })
        });

        if (res.ok) {
            alert("Instructor updated!");
            loadInstructors();
        } else {
            alert("Update failed");
        }

    } catch {
        alert("Server error");
    }
}

async function deleteClass(id) {
    if (!confirm("Delete this class?")) return;

    try {
        await fetch(`http://127.0.0.1:5000/api/classes/${id}`, {
            method: "DELETE"
        });

        alert("Class deleted!");
        loadClasses();

    } catch {
        alert("Delete failed");
    }
}

async function editClass(id, section, room, schedule) {

    const newSection = prompt("Section:", section);
    const newRoom = prompt("Room:", room);
    const newSchedule = prompt("Schedule:", schedule);

    if (!newSection || !newSchedule) return;

    try {
        const res = await fetch(`http://127.0.0.1:5000/api/classes/${id}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                section: newSection,
                room: newRoom,
                schedule: newSchedule
            })
        });

        if (res.ok) {
            alert("Class updated!");
            loadClasses();
        } else {
            alert("Update failed");
        }

    } catch {
        alert("Server error");
    }
}
window.addEventListener("DOMContentLoaded", () => {
    loadClasses();
    loadStudents();
    loadSubjects();
    loadInstructors();
    loadPrograms();
});