# KaruNature LMS — Frontend

A complete, pure HTML/CSS/JavaScript frontend for the **Karatina University Nature Club Learning Management System**.

## 📁 Folder Structure

```
frontend/
├── css/
│   └── style.css           ← Master stylesheet (all theme tokens, components, utilities)
├── js/
│   └── main.js             ← Shared JavaScript (dark mode, navbar, tabs, modals, toasts, etc.)
├── index.html              ← Homepage (hero, courses, stats, testimonials, FAQ, contact)
├── login.html              ← Login page
├── register.html           ← Registration page (Student / Instructor role)
├── courses.html            ← Courses listing with filters & search
├── course-detail.html      ← Course learning page (lessons, video, tabs, discussion)
├── student-dashboard.html  ← Student dashboard (overview, courses, assignments, certs)
├── instructor-dashboard.html ← Instructor dashboard (create courses, grade, students)
├── admin-dashboard.html    ← Admin dashboard (user mgmt, approvals, reports)
├── about.html              ← About the Nature Club
├── team.html               ← Team members page
├── contact.html            ← Contact form page
├── testimonials.html       ← Student testimonials
├── verify-certificate.html ← Certificate verification tool
└── profile.html            ← User profile settings
```

## 🎨 Design System

| Token | Value |
|-------|-------|
| Forest (primary) | `#1b4332` |
| Forest Mid | `#2d6a4f` |
| Sage | `#40916c` |
| Mint | `#52b788` |
| Lime (accent) | `#74c69d` |
| Cream (bg) | `#f8f9f4` |
| Earth | `#d4a373` |

**Fonts:** Inter (body) · Playfair Display (headings)  
**Icons:** Font Awesome 6.5

## 🖼️ Assets

All images are loaded from: `static/images/pics/`

| File | Usage |
|------|-------|
| `logo.png` | Main logo (navbar, footer, hero) |
| `graphic design.jpg` | Graphic Design course thumbnail |
| `video editting.jpg` | Videography course thumbnail |
| `web design.jpg` | Web Design course thumbnail |
| `web development.jpg` | Web Development course thumbnail |
| `online marketing.jpg` | Online Marketing thumbnail |
| `carousel 1.jpg` | Photography / Hero carousel |
| `carousel 2.jpg` | Advanced Videography thumbnail |
| `madam pj.jpg` | Testimonial — Madam PJ |
| `bwana sg.jpg` | Testimonial — Bwana SG |
| `comp m.jpg` | Testimonial — Computer Morris |
| `fmm.jpg` | Testimonial — F.M.M |
| `KEN IN.jpg` | Team — Kennedy Mwangi |
| `KINGS IN.jpg` | Team — Kings Mwangi |
| `STAR IN.jpg` | Team — Star Wanjiru |
| `KAJUNIOUR IN (2).jpg` | Team — Kajunior |
| `about.jpg` | About page hero image |

## ⚡ Features

- 🌙 **Dark Mode** — persisted in localStorage, auto-detects system preference
- 📱 **Responsive** — mobile-first, hamburger menu, collapsible sidebar
- 🎭 **Animations** — scroll-reveal, counter animation, progress bars, particle hero
- 🔔 **Toast Notifications** — success/error/warning/info
- 🗂️ **Tabs** — reusable tab component
- 🗃️ **Modals** — accessible modal overlays
- 🔍 **Course Filter** — real-time filter by category, difficulty + search
- ✅ **FAQ Accordion** — smooth open/close
- 📊 **Dashboard Panels** — sidebar nav switching panels

## 🔗 Navigation Map

```
index.html
  ├── login.html
  ├── register.html
  ├── courses.html → course-detail.html
  ├── about.html
  ├── team.html
  ├── testimonials.html
  ├── contact.html
  └── verify-certificate.html

(After login)
  ├── student-dashboard.html → profile.html
  ├── instructor-dashboard.html
  └── admin-dashboard.html
```

## 🔧 Backend Integration

All forms currently show demo toasts. To connect to your backend:
1. Replace form `action=""` with your API endpoint URLs
2. Replace `fetch()`/`XMLHttpRequest` calls where toast demos exist
3. Populate data (courses, users, etc.) dynamically via template engine or JS fetch

## Deploying on Vercel

This is a static HTML/CSS/JavaScript frontend and does not require a build step. Import the repository into Vercel with the repository root as the project root; `vercel.json` publishes the `frontend/` directory. The site entry point is `index.html`.

The forms and login screens are frontend demos. Deploying this site does not provide backend authentication, persistent data, or form submission services.

---

*Built with ❤️ for Karatina University Nature Club*
