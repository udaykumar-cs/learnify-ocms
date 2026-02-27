const button = document.getElementById("loadCourses");
const list = document.getElementById("coursesList");

button?.addEventListener("click", async () => {
  list.innerHTML = "<li>Loading...</li>";
  try {
    const response = await fetch("/api/courses/courses/?is_published=true");
    const data = await response.json();
    const rows = data.results || [];
    if (!rows.length) {
      list.innerHTML = "<li>No published courses available.</li>";
      return;
    }
    list.innerHTML = rows
      .map((course) => `<li><strong>${course.title}</strong> - ${course.level} - $${course.price}</li>`)
      .join("");
  } catch (error) {
    list.innerHTML = "<li>Unable to load courses right now.</li>";
  }
});
