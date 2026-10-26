export function normalizeGreek(value) {
  return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLocaleLowerCase('el').replace(/ς/g, 'σ').trim();
}

export function filterCategories(categories, query, categoryId) {
  const terms = normalizeGreek(query).split(/\s+/).filter(Boolean);
  return categories.filter(category => !categoryId || category.id === categoryId)
    .map(category => ({
      ...category,
      lessons: category.lessons.filter(lesson => {
        const searchable = normalizeGreek([
          category.title, lesson.title, lesson.description, ...lesson.topics,
        ].join(' '));
        return terms.every(term => searchable.includes(term));
      }),
    })).filter(category => category.lessons.length > 0);
}
