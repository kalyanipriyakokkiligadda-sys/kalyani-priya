const API_URL = "http://127.0.0.1:5000";

/* ================= TAB SWITCH ================= */
function switchTab(tab) {
  const loginForm = document.getElementById("loginForm");
  const signupForm = document.getElementById("signupForm");
  const tabs = document.querySelectorAll(".tab");

  tabs.forEach(t => t.classList.remove("active"));

  if (tab === "login") {
    loginForm.classList.remove("hidden");
    signupForm.classList.add("hidden");
    tabs[0].classList.add("active");
  } else {
    signupForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
    tabs[1].classList.add("active");
  }
}

/* ================= LOGIN ================= */
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  const res = await fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (res.ok) {
    localStorage.setItem("token", data.token);
    localStorage.setItem("username", data.user.username);
    window.location.href = "/dashboard_page";
  } else {
    document.getElementById("loginError").innerText = data.error;
    document.getElementById("loginError").classList.remove("hidden");
  }
});

/* ================= SIGNUP ================= */
document.getElementById("signupForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = document.getElementById("signupUsername").value;
  const email = document.getElementById("signupEmail").value;
  const password = document.getElementById("signupPassword").value;

  const res = await fetch(`${API_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, email, password })
  });

  const data = await res.json();

  if (res.ok) {
    localStorage.setItem("token", data.token);
    localStorage.setItem("username", username);
    window.location.href = "/dashboard_page";
  } else {
    document.getElementById("signupError").innerText = data.error;
    document.getElementById("signupError").classList.remove("hidden");
  }
});

/* ================= LOGOUT ================= */
function logout() {
  localStorage.clear();
  window.location.href = "/";
}

/* ================= CREATE TASK ================= */
document.getElementById("taskForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();

  const token = localStorage.getItem("token");

  const titleInput = document.getElementById("taskTitle");
  const descInput = document.getElementById("taskDesc");
  const dueInput = document.getElementById("taskDue");
  const priorityInput = document.getElementById("taskPriority");
  const statusInput = document.getElementById("taskStatus");

  await fetch(`${API_URL}/create_task`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": token
    },
    body: JSON.stringify({
      title: titleInput.value,
      description: descInput.value,
      duedate: dueInput.value,
      priority: priorityInput.value,
      status: statusInput.value
    })
  });

  // 🔥 FORCE CLEAR EVERYTHING
  titleInput.value = "";
  descInput.value = "";
  dueInput.value = "";
  priorityInput.value = "medium";
  statusInput.value = "pending";

  closeModal();
  loadTasks();
});
function openModal() {
  document.getElementById("taskTitle").value = "";
  document.getElementById("taskDesc").value = "";
  document.getElementById("taskDue").value = "";
  document.getElementById("taskPriority").value = "medium";
  document.getElementById("taskStatus").value = "pending";

  document.getElementById("modalOverlay").classList.remove("hidden");
}
function closeModal() {
  document.getElementById("modalOverlay").classList.add("hidden");
}
/* ================= LOAD TASKS ================= */
async function loadTasks() {
  const token = localStorage.getItem("token");
  if (!token) return;

  const res = await fetch(`${API_URL}/get_task`, {
    headers: { "Authorization": token }
  });

  const tasks = await res.json();
  renderTasks(tasks);
}

/* ================= RENDER TASKS ================= */
function renderTasks(tasks) {
  const grid = document.getElementById("taskGrid");
  const count = document.getElementById("taskCount");

  grid.innerHTML = "";

  if (tasks.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <span>📭</span>
        <p>No tasks yet. Create your first task!</p>
      </div>
    `;
  } else {
    tasks.forEach(task => {
      const card = document.createElement("div");
      card.className = "task-card";

      card.innerHTML = `
        <h4>${task.title}</h4>
        <p>${task.description}</p>
        <small>Due: ${task.duedate}</small>
        <div class="task-footer">
          <span class="badge ${task.priority}">${task.priority}</span>
          <span class="status">${task.status}</span>
          <button onclick="deleteTask(${task.task_id})">🗑</button>
        </div>
      `;

      grid.appendChild(card);
    });
  }

  count.innerText = `${tasks.length} tasks`;
}
/* ✅ PASTE DELETE FUNCTION RIGHT HERE */
async function deleteTask(id) {
  const token = localStorage.getItem("token");

  await fetch(`${API_URL}/task_delete?task_id=${id}`, {
    method: "DELETE",
    headers: {
      "Authorization": token
    }
  });

  loadTasks();
}

/* ================= AUTO LOAD DASHBOARD ================= */
if (window.location.pathname.includes("dashboard_page")) {

  if (!localStorage.getItem("token")) {
    window.location.href = "/";
  }

  document.getElementById("sidebarUsername").innerText =
    localStorage.getItem("username");

  loadTasks();
}