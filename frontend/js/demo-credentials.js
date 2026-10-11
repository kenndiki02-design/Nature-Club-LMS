// Demo-only accounts for the frontend prototype. Do not use for real authentication.
window.NATURE_CLUB_DEMO_CREDENTIALS = Object.freeze([
  Object.freeze({
    role: 'admin',
    email: 'admin@natureclub.test',
    password: 'AdminDemo123!',
    dashboard: 'admin-dashboard.html'
  }),
  Object.freeze({
    role: 'instructor',
    email: 'instructor@natureclub.test',
    password: 'InstructorDemo123!',
    dashboard: 'instructor-dashboard.html'
  }),
  Object.freeze({
    role: 'student',
    email: 'student@natureclub.test',
    password: 'StudentDemo123!',
    dashboard: 'student-dashboard.html'
  })
]);