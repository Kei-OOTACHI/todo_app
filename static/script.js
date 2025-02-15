// タスク追加機能
document.getElementById("add-task-form").onsubmit = function (event) {
  event.preventDefault();
  const content = document.getElementById("task-content").value;
  const deadline = document.getElementById("task-deadline").value;
  const category = document.getElementById("task-category").value;
  const assigneeEmail = document.getElementById("task-assignee-email").value;

  fetch("/api/tasks2", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify([
      { content, deadline, category, assignee_email: assigneeEmail },
    ]), // 辞書のリストとして送信
  })
    .then((response) => {
      if (response.status === 400) {
        return response.json().then((data) => {
          throw new Error(data.error);
        });
      }
      return response.json();
    })
    .then((data) => {
      alert("タスクが追加されました: " + JSON.stringify(data));
    })
    .catch((error) => {
      alert("エラーが発生しました: " + error.message);
    });
};

// タスク取得機能
document.getElementById("get-task-form").onsubmit = function (event) {
  event.preventDefault();
  const taskId = document.getElementById("task-id").value;
  fetch(`/api/tasks2/${taskId}`)
    .then((response) => {
      if (response.status === 200) {
        return response.json();
      } else if (response.status === 404) {
        alert("タスクが見つかりません");
        throw new Error("Not found");
      } else {
        throw new Error("Error");
      }
    })
    .then((data) => {
      document.getElementById("task-display").textContent = `ID: ${
        data.id
      }, 内容: ${data.content}, 完了: ${data.done ? "はい" : "いいえ"}, 〆切: ${
        data.deadline
      }, 作成日: ${data.created_at}, 変更日: ${data.updated_at}, カテゴリー: ${
        data.category
      }, 担当者メールアドレス: ${data.assignee_email}`;
    })
    .catch((error) => {
      document.getElementById("task-display").textContent =
        "エラーが発生しました";
    });
};

// タスク更新機能
document.getElementById("update-task-form").onsubmit = function (event) {
  event.preventDefault();
  const taskId = document.getElementById("update-task-id").value;
  const content = document.getElementById("update-task-content").value;
  const done = document.getElementById("update-task-done").checked;
  const deadline = document.getElementById("update-task-deadline").value;
  const category = document.getElementById("update-task-category").value;
  const assigneeEmail = document.getElementById(
    "update-task-assignee-email"
  ).value;

  fetch(`/api/tasks2`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify([
      {
        id: taskId,
        content,
        done,
        deadline,
        category,
        assignee_email: assigneeEmail,
      },
    ]), // 辞書のリストとして送信
  })
    .then((response) => {
      if (response.status === 400) {
        return response.json().then((data) => {
          throw new Error(data.error);
        });
      } else if (response.status === 204) {
        alert("タスクが更新されました");
      } else {
        throw new Error("Error");
      }
    })
    .catch((error) => {
      alert("エラーが発生しました: " + error.message);
    });
};

// タスク削除機能
document.getElementById("delete-task-form").onsubmit = function (event) {
  event.preventDefault();
  const taskId = document.getElementById("delete-task-id").value;

  fetch(`/api/tasks2`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify([taskId]), // IDのリストとして送信
  })
    .then((response) => {
      if (response.status === 204) {
        alert("タスクが削除されました");
      } else if (response.status === 404) {
        alert("タスクが見つかりません");
        throw new Error("Not found");
      } else {
        throw new Error("Error");
      }
    })
    .catch((error) => {
      alert("エラーが発生しました: " + error.message);
    });
};

// タスク一覧表示機能
document.getElementById("list-tasks-button").onclick = function () {
  fetch("/api/tasks2")
    .then((response) => response.json())
    .then((data) => {
      const tasksList = document.getElementById("tasks-display");
      tasksList.innerHTML = ""; // 既存のタスクリストをクリア
      data.tasks.forEach((task) => {
        const li = document.createElement("li");
        li.textContent = `ID: ${task.id}, 内容: ${task.content}, 完了: ${
          task.done ? "はい" : "いいえ"
        }, 〆切: ${task.deadline}, 作成日: ${task.created_at}, 変更日: ${
          task.updated_at
        }, カテゴリー: ${task.category}, 担当者メールアドレス: ${
          task.assignee_email
        }`;
        tasksList.appendChild(li);
      });
    })
    .catch((error) => {
      alert("エラーが発生しました: " + error.message);
    });
};
