// Topics in reading order. A page shows up in the sidebar once its file exists.
// Kept free of Node imports so the browser code can use it too.
export const groups: { en: string; ar: string; slugs: string[] }[] = [
  {
    en: 'Arriving',
    ar: 'الوصول',
    slugs: ['arriving-and-visas', 'residence-permit-and-qid', 'metrash', 'family-visas']
  },
  {
    en: 'Settling in',
    ar: 'الاستقرار',
    slugs: ['housing-and-utilities', 'health', 'phone-and-internet', 'banking-and-money']
  },
  {
    en: 'Work and money',
    ar: 'العمل والمال',
    slugs: ['work-and-labour-rights', 'cost-of-living', 'holidays-and-ramadan']
  },
  {
    en: 'Daily life',
    ar: 'الحياة اليومية',
    slugs: ['driving', 'transport', 'education', 'emergencies']
  }
]
