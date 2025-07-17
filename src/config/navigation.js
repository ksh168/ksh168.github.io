import Home from '../pages/home';
import Education from '../pages/education';
// import Experience from '../pages/experience';
import Projects from '../pages/projects';
import Contact from '../pages/contact';
import Publications from '../pages/publications';

export const navigationLinks = [
  { path: '/', label: 'Home', component: Home },
  { path: '/education', label: 'Education', component: Education },
  { path: '/publications', label: 'Publications', component: Publications },
  // { path: '/experience', label: 'Experience', component: Experience },
  { path: '/projects', label: 'Projects', component: Projects },
  { path: '/contact', label: 'Contact', component: Contact },
];