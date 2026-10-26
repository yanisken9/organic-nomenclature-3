import React, { useRef } from 'react';
import { filterCategories } from './library-search.js';

function Formula({ formula }) {
  if (!formula) return null;
  return <p className="series-formula">
    {formula.parts.map((part, index) => part.kind === 'subscript'
      ? <sub key={index}>{part.value}</sub>
      : <React.Fragment key={index}>{part.value}</React.Fragment>)}
    {formula.restriction && <span className="restriction">{formula.restriction}</span>}
  </p>;
}

function Lesson({ lesson, resolveHref, grouped }) {
  const titleId = `${lesson.id}-title`;
  const body = <>
    <h3 id={titleId} className="catalog-lesson-title">{lesson.title}</h3>
    <Formula formula={lesson.formula} />
    <p>{lesson.description}</p>
    {grouped && <p><span className="count">{lesson.steps} βήματα</span></p>}
    {lesson.topics.length > 0 && <ul className="topics">
      {lesson.topics.map(topic => <li key={topic}>{topic}</li>)}
    </ul>}
    <a className="action" href={resolveHref(lesson.href)}>
      {lesson.actionLabel}<span aria-hidden="true">→</span>
    </a>
  </>;
  return grouped ? <section className="lesson-part" aria-labelledby={titleId}>{body}</section> : body;
}

function LessonCard({ category, original, resolveHref }) {
  const headingId = `${category.id}-category-title`;
  const grouped = original.lessons.length > 1;
  const partial = category.lessons.length !== original.lessons.length;
  return <article className="lesson" aria-labelledby={headingId} data-category={category.id}>
    <div className={`illustration ${grouped ? 'alcohols-header' : 'series-header'}`}>
      <div className="series-heading">
        <h2 id={headingId} className="formula catalog-category-title">{category.title}</h2>
        <Formula formula={category.formula} />
      </div>
      <span className="count">{partial
        ? `${category.lessons.length} από ${original.lessons.length} μαθήματα`
        : original.summaryLabel}</span>
    </div>
    <div className={`content ${grouped ? '' : 'catalog-single'}`}>
      {category.lessons.map(lesson => <Lesson key={lesson.id} lesson={lesson}
        resolveHref={resolveHref} grouped={grouped} />)}
    </div>
  </article>;
}

export default function LibraryPage({ catalog, filters, setFilters, resolveHref }) {
  const search = useRef(null);
  const visible = filterCategories(catalog.categories, filters.query, filters.categoryId);
  const lessonCount = visible.reduce((sum, category) => sum + category.lessons.length, 0);
  const active = Boolean(filters.query || filters.categoryId);
  function clear() {
    setFilters({ query: '', categoryId: '' });
    search.current.focus();
  }
  return <main>
    <span className="eyebrow">{catalog.eyebrow}</span>
    <h1>{catalog.heading}</h1>
    <p className="intro">{catalog.intro}</p>
    <form className="catalog-controls" role="search" onSubmit={event => event.preventDefault()}>
      <div className="catalog-search-field">
        <label htmlFor="lesson-search">Αναζήτηση μαθημάτων</label>
        <input ref={search} id="lesson-search" type="search" autoComplete="off"
          placeholder="π.χ. αλκοόλες ή αλκύλια" aria-describedby="lesson-search-hint"
          value={filters.query} onChange={event => setFilters({ ...filters, query: event.target.value })} />
      </div>
      <div className="catalog-category-field">
        <label htmlFor="lesson-category">Κατηγορία</label>
        <select id="lesson-category" value={filters.categoryId}
          onChange={event => setFilters({ ...filters, categoryId: event.target.value })}>
          <option value="">Όλες οι κατηγορίες</option>
          {catalog.categories.map(category => <option key={category.id} value={category.id}>{category.title}</option>)}
        </select>
      </div>
      <button type="button" className="catalog-clear" disabled={!active} onClick={clear}>Καθαρισμός</button>
      <p id="lesson-search-hint" className="catalog-hint">Αναζήτηση σε τίτλους, περιγραφές και θέματα μαθημάτων.</p>
    </form>
    <p className="catalog-results" role="status" aria-live="polite" aria-atomic="true">
      {lessonCount} {lessonCount === 1 ? 'μάθημα' : 'μαθήματα'} σε {visible.length} {visible.length === 1 ? 'κατηγορία' : 'κατηγορίες'}
    </p>
    {visible.length > 0 ? <section className="lessons" aria-label="Διαθέσιμα μαθήματα">
      {visible.map(category => <LessonCard key={category.id} category={category}
        original={catalog.categories.find(item => item.id === category.id)} resolveHref={resolveHref} />)}
    </section> : <p className="catalog-empty">Δεν βρέθηκαν μαθήματα. Δοκίμασε διαφορετική αναζήτηση ή κατηγορία.</p>}
  </main>;
}
