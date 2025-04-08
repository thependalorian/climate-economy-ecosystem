// Navigation items for authenticated users
const authenticatedNavItems = [
  { 
    label: 'Dashboard', 
    href: '/dashboard', 
    icon: 'dashboard' 
  },
  { 
    label: 'Profile', 
    href: '/profile',
    icon: 'profile',
    subItems: [
      { label: 'View Profile', href: '/profile' },
      { label: 'Edit Profile', href: '/profile/edit' },
      { label: 'Enhance Profile', href: '/profile/enrich' }
    ]
  },
  { 
    label: 'Jobs', 
    href: '/jobs',
    icon: 'briefcase',
    subItems: [
      { label: 'Job Board', href: '/jobs' },
      { label: 'Enhanced Search', href: '/jobs/enhanced-search' },
      { label: 'Saved Jobs', href: '/jobs/saved' }
    ]
  },
  // ... other existing nav items ...
]; 