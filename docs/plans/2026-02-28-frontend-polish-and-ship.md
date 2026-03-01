# Frontend Polish & Ship Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Polish the frontend redesign with premium visual treatment (gradients, glassmorphism, animations) and ship it to main.

**Architecture:** CSS-only visual layer changes on top of existing component architecture. Update globals.css CSS variables, tailwind.config.cjs theme extensions, and component className strings. No structural/logic changes to components or hooks.

**Tech Stack:** Tailwind CSS, CSS custom properties, CSS transitions/animations, existing shadcn/ui + Radix primitives.

---

### Task 1: Extend the design token system in globals.css

**Files:**
- Modify: `frontend/src/globals.css`

**Step 1: Update CSS variables for richer color palette**

Replace the full `:root` block with an expanded set of design tokens:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 210 20% 98%;
    --foreground: 220 14% 10%;
    --card: 0 0% 100%;
    --card-foreground: 220 14% 10%;
    --popover: 0 0% 100%;
    --popover-foreground: 220 14% 10%;
    --primary: 172 66% 30%;
    --primary-foreground: 0 0% 98%;
    --secondary: 220 14% 96%;
    --secondary-foreground: 220 14% 10%;
    --muted: 220 14% 96%;
    --muted-foreground: 220 8% 46%;
    --accent: 220 14% 96%;
    --accent-foreground: 220 14% 10%;
    --destructive: 0 84% 60%;
    --destructive-foreground: 0 0% 98%;
    --border: 220 13% 91%;
    --input: 220 13% 91%;
    --ring: 172 66% 30%;
    --radius: 0.625rem;

    /* Premium accents */
    --gradient-start: 172 66% 30%;
    --gradient-end: 199 89% 48%;
    --glass-bg: 0 0% 100% / 0.7;
    --glass-border: 0 0% 100% / 0.2;
    --sidebar-bg: 220 20% 97%;
    --glow-primary: 172 66% 30% / 0.15;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground antialiased;
    font-feature-settings: "rlig" 1, "calt" 1;
  }
}

/* Utility classes for premium effects */
@layer utilities {
  .glass {
    background: hsl(var(--glass-bg));
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
  }
  .gradient-primary {
    background: linear-gradient(135deg, hsl(var(--gradient-start)), hsl(var(--gradient-end)));
  }
  .gradient-text {
    background: linear-gradient(135deg, hsl(var(--gradient-start)), hsl(var(--gradient-end)));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .glow-sm {
    box-shadow: 0 0 12px hsl(var(--glow-primary));
  }
  .glow-md {
    box-shadow: 0 0 24px hsl(var(--glow-primary));
  }
}
```

**Step 2: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds with no errors.

**Step 3: Commit**

```bash
git add frontend/src/globals.css
git commit -m "feat(frontend): expand design tokens with premium color palette and utility classes"
```

---

### Task 2: Extend Tailwind config with animation utilities

**Files:**
- Modify: `frontend/tailwind.config.cjs`

**Step 1: Add keyframes and animation extensions**

Replace the full `tailwind.config.cjs`:

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      keyframes: {
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "slide-in-left": {
          "0%": { opacity: "0", transform: "translateX(-12px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        "scale-in": {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "shimmer": {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "progress-glow": {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        "check-appear": {
          "0%": { opacity: "0", transform: "scale(0) rotate(-45deg)" },
          "50%": { transform: "scale(1.2) rotate(0deg)" },
          "100%": { opacity: "1", transform: "scale(1) rotate(0deg)" },
        },
      },
      animation: {
        "fade-in-up": "fade-in-up 0.3s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
        "slide-in-left": "slide-in-left 0.3s ease-out",
        "scale-in": "scale-in 0.2s ease-out",
        "shimmer": "shimmer 2s linear infinite",
        "progress-glow": "progress-glow 2s ease-in-out infinite",
        "check-appear": "check-appear 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)",
      },
    },
  },
  plugins: [],
};
```

**Step 2: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds.

**Step 3: Commit**

```bash
git add frontend/tailwind.config.cjs
git commit -m "feat(frontend): add animation keyframes and premium utility extensions to Tailwind config"
```

---

### Task 3: Polish the Sidebar and DocumentListItemCard

**Files:**
- Modify: `frontend/src/components/layout/Sidebar.tsx`
- Modify: `frontend/src/components/layout/DocumentListItemCard.tsx`
- Modify: `frontend/src/components/layout/AppShell.tsx`

**Step 1: Update AppShell with subtle background treatment**

In `AppShell.tsx`, update the outer div className:

```tsx
<div className="flex h-screen w-screen overflow-hidden bg-background">
```
Change to:
```tsx
<div className="flex h-screen w-screen overflow-hidden bg-[hsl(var(--sidebar-bg))]">
```

**Step 2: Update Sidebar with gradient header and refined styling**

Replace the `aside` element content in `Sidebar.tsx`:

```tsx
<aside className="flex w-[280px] shrink-0 flex-col border-r bg-card/80 backdrop-blur-sm">
  {/* Logo area */}
  <div className="flex items-center gap-2.5 px-5 py-5">
    <div className="gradient-primary flex h-8 w-8 items-center justify-center rounded-lg shadow-sm">
      <Layers className="h-4 w-4 text-white" />
    </div>
    <div>
      <h1 className="text-base font-semibold tracking-tight">SlideNode</h1>
      <p className="text-[11px] text-muted-foreground">PDF to learning slides</p>
    </div>
  </div>

  <div className="px-3 pb-3">
    <Button
      onClick={onUploadClick}
      className="gradient-primary w-full gap-2 border-0 shadow-sm transition-all duration-300 hover:shadow-md hover:brightness-110"
    >
      <FileUp className="h-4 w-4" />
      New Document
    </Button>
  </div>

  <Separator />

  {/* Document list */}
  <ScrollArea className="flex-1">
    <div className="p-3 space-y-1">
      {documents.length === 0 ? (
        <p className="px-2 py-8 text-center text-sm text-muted-foreground">
          No documents yet
        </p>
      ) : (
        documents.map((doc) => (
          <DocumentListItemCard
            key={doc.id}
            document={doc}
            isActive={doc.id === activeDocumentId}
            isProcessing={
              doc.id === activeDocumentId &&
              job !== null &&
              (job.status === "queued" || job.status === "running")
            }
            progress={
              doc.id === activeDocumentId && job ? job.progress : undefined
            }
            onClick={() => onOpenDocument(doc.id)}
            onDelete={() => onDeleteDocument(doc.id)}
          />
        ))
      )}
    </div>
  </ScrollArea>
</aside>
```

**Step 3: Update DocumentListItemCard with hover lift and refined active state**

Replace the outer `div` className logic in `DocumentListItemCard.tsx`:

```tsx
<div
  className={`
    group relative flex flex-col gap-1 rounded-lg px-3 py-2.5 cursor-pointer
    transition-all duration-300
    ${isActive
      ? "bg-gradient-to-r from-primary/8 to-primary/4 border border-primary/20 shadow-sm"
      : "hover:bg-card hover:shadow-sm border border-transparent hover:border-border/50"
    }
  `}
  onClick={onClick}
  onMouseEnter={() => setIsHovered(true)}
  onMouseLeave={() => setIsHovered(false)}
>
```

Update the icon container:
```tsx
<div
  className={`
    mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md
    transition-all duration-300
    ${isActive
      ? "gradient-primary text-white shadow-sm"
      : "bg-muted text-muted-foreground"
    }
  `}
>
```

**Step 4: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds.

**Step 5: Commit**

```bash
git add frontend/src/components/layout/
git commit -m "feat(frontend): premium sidebar with gradient header, card hover effects, and refined active states"
```

---

### Task 4: Polish the EmptyState and ProcessingState

**Files:**
- Modify: `frontend/src/components/main/EmptyState.tsx`
- Modify: `frontend/src/components/main/ProcessingState.tsx`
- Modify: `frontend/src/components/ui/progress.tsx`

**Step 1: Update EmptyState with gradient icon and fade-in animation**

Replace full `EmptyState.tsx` return:

```tsx
export function EmptyState() {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-5 text-center animate-fade-in">
      <div className="gradient-primary flex h-16 w-16 items-center justify-center rounded-2xl shadow-lg">
        <FileText className="h-7 w-7 text-white" />
      </div>
      <div>
        <h2 className="text-lg font-semibold text-foreground">No document selected</h2>
        <p className="mt-1.5 max-w-[280px] text-sm text-muted-foreground leading-relaxed">
          Upload a PDF or select a document from the sidebar to get started.
        </p>
      </div>
    </div>
  );
}
```

**Step 2: Update Progress component with gradient fill and glow**

Replace the `ProgressPrimitive.Indicator` className in `frontend/src/components/ui/progress.tsx`:

```tsx
<ProgressPrimitive.Indicator
  className="h-full w-full flex-1 gradient-primary transition-all duration-500 ease-out"
  style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
/>
```

**Step 3: Update ProcessingState with animated pipeline and refined styling**

In `ProcessingState.tsx`, update the active spinner container:

```tsx
<div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 glow-sm">
  <Loader2 className="h-6 w-6 animate-spin text-primary" />
</div>
```

Update the pipeline step list checkmark (the `isDone && !isCurrent` case):

```tsx
{isDone && !isCurrent ? (
  <svg className="h-3 w-3 text-primary animate-check-appear" viewBox="0 0 12 12" fill="none">
    <path d="M2 6l3 3 5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
) : isCurrent ? (
  <Loader2 className="h-3 w-3 animate-spin text-primary" />
) : (
  <span className="h-1.5 w-1.5 rounded-full bg-current opacity-40" />
)}
```

Update each pipeline step item className:

```tsx
<div
  key={step.threshold}
  className={`
    flex items-center gap-2 text-xs transition-all duration-300
    ${isCurrent ? "text-foreground font-medium translate-x-1" : isDone ? "text-muted-foreground" : "text-muted-foreground/30"}
  `}
>
```

**Step 4: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds.

**Step 5: Commit**

```bash
git add frontend/src/components/main/ frontend/src/components/ui/progress.tsx
git commit -m "feat(frontend): animated processing pipeline, gradient progress bar, and polished empty state"
```

---

### Task 5: Polish the Editor Toolbar

**Files:**
- Modify: `frontend/src/components/editor/EditorToolbar.tsx`
- Modify: `frontend/src/components/shared/QualityBadge.tsx`

**Step 1: Update EditorToolbar with subtle gradient bottom border**

Replace the toolbar outer div:

```tsx
<div className="relative flex shrink-0 items-center justify-between border-b px-5 py-3 bg-card/50 backdrop-blur-sm">
```

Update the Save button to be gradient when dirty:

```tsx
<Button
  variant={isDirty ? "default" : "outline"}
  size="sm"
  onClick={onSave}
  disabled={!isDirty}
  className={`
    gap-1.5 transition-all duration-300
    ${isDirty ? "gradient-primary border-0 shadow-sm hover:shadow-md hover:brightness-110" : ""}
  `}
>
  <Save className="h-3.5 w-3.5" />
  Save
</Button>
```

**Step 2: Update QualityBadge with refined gradient styling**

Replace the Badge className logic in `QualityBadge.tsx`:

```tsx
<Badge
  variant={isGood ? "secondary" : "destructive"}
  className={`
    cursor-default text-[11px] font-medium transition-all duration-200
    ${isGood
      ? "bg-emerald-50 text-emerald-700 border-emerald-200/60 shadow-sm shadow-emerald-100"
      : "bg-red-50 text-red-700 border-red-200/60 shadow-sm shadow-red-100"
    }
  `}
>
  {label} {percent}%
</Badge>
```

**Step 3: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds.

**Step 4: Commit**

```bash
git add frontend/src/components/editor/EditorToolbar.tsx frontend/src/components/shared/QualityBadge.tsx
git commit -m "feat(frontend): polished editor toolbar with gradient save button and refined quality badges"
```

---

### Task 6: Polish the DeckEditor dual pane, SectionBlock, and SubsectionBlock

**Files:**
- Modify: `frontend/src/components/editor/DeckEditorDualPane.tsx`
- Modify: `frontend/src/components/editor/SlidePane.tsx`
- Modify: `frontend/src/components/editor/SectionBlock.tsx`
- Modify: `frontend/src/components/editor/SubsectionBlock.tsx`
- Modify: `frontend/src/components/editor/BulletItem.tsx`

**Step 1: Refine DeckEditorDualPane divider styling**

In `DeckEditorDualPane.tsx`, update the citation pane container:

```tsx
{/* Citation Pane - Left (40%) */}
<div className="w-[40%] shrink-0 overflow-hidden border-r border-border/50 bg-muted/20">
```

**Step 2: Add staggered fade-in to SlidePane sections**

In `SlidePane.tsx`, add animation to each section via inline style:

```tsx
{draftSections.map((draft, idx) => {
  const section = deck.sections[idx];
  if (!section) return null;
  return (
    <div
      key={draft.id}
      className="animate-fade-in-up"
      style={{ animationDelay: `${idx * 60}ms`, animationFillMode: "both" }}
    >
      <SectionBlock
        section={section}
        draft={draft}
        activeBulletId={activeBulletId}
        onSectionHeadingChange={(h) => onUpdateSectionHeading(draft.id, h)}
        onSubsectionHeadingChange={(subId, h) => onUpdateSubsectionHeading(draft.id, subId, h)}
        onSubsectionAnnotationChange={(subId, a) => onUpdateSubsectionAnnotation(draft.id, subId, a)}
        onBulletTextChange={(subId, bId, text) => onUpdateBulletText(draft.id, subId, bId, text)}
        onBulletFocus={onBulletFocus}
      />
    </div>
  );
})}
```

**Step 3: Polish SectionBlock with refined card and section number**

In `SectionBlock.tsx`, update the outer card div and trigger:

```tsx
<Collapsible open={isOpen} onOpenChange={setIsOpen}>
  <div className="rounded-xl border bg-card shadow-sm transition-all duration-300 hover:shadow-md">
    <CollapsibleTrigger asChild>
      <div className="flex items-center gap-2.5 px-4 py-3 cursor-pointer select-none">
        <div className={`
          flex h-5 w-5 items-center justify-center rounded transition-transform duration-300
          ${isOpen ? "rotate-0" : "-rotate-90"}
        `}>
          <ChevronDown className="h-4 w-4 text-muted-foreground" />
        </div>
        <input
          type="text"
          value={draft.heading}
          onChange={(e) => onSectionHeadingChange(e.target.value)}
          onClick={(e) => e.stopPropagation()}
          className="flex-1 bg-transparent text-sm font-semibold tracking-tight outline-none"
          placeholder="Section heading"
        />
        <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground shrink-0">
          {section.subsections.length} subsection{section.subsections.length !== 1 ? "s" : ""}
        </span>
      </div>
    </CollapsibleTrigger>

    <CollapsibleContent>
      <div className="space-y-4 px-4 pb-4 pt-1">
```

Remove the `ChevronRight` import — only `ChevronDown` is needed since we use rotation.

**Step 4: Polish BulletItem with refined active glow**

In `BulletItem.tsx`, update the outer div:

```tsx
<div
  className={`
    group flex items-start gap-2 rounded-lg px-2.5 py-2
    transition-all duration-200
    ${isActive ? "bg-primary/6 shadow-sm shadow-primary/5" : "hover:bg-muted/50"}
  `}
>
```

Update the bullet dot:

```tsx
<span className={`
  mt-2 h-1.5 w-1.5 shrink-0 rounded-full transition-colors duration-200
  ${isActive ? "bg-primary" : "bg-foreground/25"}
`} />
```

Update the citation Badge:

```tsx
<Badge
  variant="outline"
  className={`
    shrink-0 text-[10px] font-mono cursor-default transition-all duration-200
    ${isActive ? "border-primary/30 bg-primary/5 text-primary" : "text-muted-foreground/60 border-border/50"}
  `}
>
  {citationCount}
</Badge>
```

**Step 5: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds.

**Step 6: Commit**

```bash
git add frontend/src/components/editor/DeckEditorDualPane.tsx frontend/src/components/editor/SlidePane.tsx frontend/src/components/editor/SectionBlock.tsx frontend/src/components/editor/SubsectionBlock.tsx frontend/src/components/editor/BulletItem.tsx
git commit -m "feat(frontend): polished editor with card shadows, staggered section animations, and active bullet glow"
```

---

### Task 7: Polish the CitationPane and CitationCard

**Files:**
- Modify: `frontend/src/components/editor/CitationPane.tsx`
- Modify: `frontend/src/components/editor/CitationCard.tsx`

**Step 1: Update CitationPane empty state with gradient icon**

In `CitationPane.tsx`, update the empty state icon container:

```tsx
<div className="gradient-primary flex h-12 w-12 items-center justify-center rounded-xl shadow-sm">
  <BookOpen className="h-5 w-5 text-white" />
</div>
```

Update the citation count label:

```tsx
<p className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground/70 mb-3">
  {activeCitations.length} citation{activeCitations.length !== 1 ? "s" : ""}
</p>
```

Wrap each citation in an animated container:

```tsx
{activeCitations.map((c, i) => (
  <div
    key={`${c.page}-${c.paragraph_index}-${i}`}
    className="animate-fade-in-up"
    style={{ animationDelay: `${i * 50}ms`, animationFillMode: "both" }}
  >
    <CitationCard citation={c} isActive={true} />
  </div>
))}
```

**Step 2: Update CitationCard with glass effect and page badge gradient**

Replace the full `CitationCard` return in `CitationCard.tsx`:

```tsx
export function CitationCard({ citation, isActive }: CitationCardProps) {
  return (
    <div
      data-citation-page={citation.page}
      className={`
        rounded-xl border p-3.5 transition-all duration-300
        ${isActive
          ? "bg-card border-primary/20 shadow-sm"
          : "border-transparent bg-muted/30 hover:bg-muted/50"
        }
      `}
    >
      <div className="flex items-start gap-2.5">
        <Badge
          className={`
            shrink-0 text-[10px] font-mono border-0 transition-colors
            ${isActive ? "gradient-primary text-white shadow-sm" : "bg-muted text-muted-foreground"}
          `}
        >
          p.{citation.page}
        </Badge>
        <p className="text-[13px] leading-relaxed text-foreground/75">
          {citation.quote_snippet}
        </p>
      </div>
    </div>
  );
}
```

**Step 3: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds.

**Step 4: Commit**

```bash
git add frontend/src/components/editor/CitationPane.tsx frontend/src/components/editor/CitationCard.tsx
git commit -m "feat(frontend): polished citation pane with gradient badges, fade-in animation, and refined cards"
```

---

### Task 8: Polish the UploadDialog and DropZone

**Files:**
- Modify: `frontend/src/components/upload/UploadDialog.tsx`
- Modify: `frontend/src/components/upload/DropZone.tsx`

**Step 1: Update UploadDialog with glass backdrop**

In `UploadDialog.tsx`, update DialogContent:

```tsx
<DialogContent className="sm:max-w-md glass border-white/20">
```

Update the Start Pipeline button:

```tsx
<Button
  onClick={handleUpload}
  disabled={!selectedFile || uploading}
  className="gradient-primary gap-2 border-0 shadow-sm transition-all duration-300 hover:shadow-md hover:brightness-110"
>
```

**Step 2: Update DropZone with refined interactions**

In `DropZone.tsx`, update the outer div className:

```tsx
<div
  className={`
    relative flex flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed
    px-6 py-10 transition-all duration-300 cursor-pointer
    ${isDragOver
      ? "border-primary bg-primary/5 scale-[1.02] shadow-lg shadow-primary/10"
      : "border-muted-foreground/20 hover:border-primary/40 hover:bg-muted/30"
    }
    ${disabled ? "opacity-50 cursor-not-allowed" : ""}
  `}
```

Update the icon circle:

```tsx
<div
  className={`
    flex h-12 w-12 items-center justify-center rounded-full transition-all duration-300
    ${isDragOver ? "gradient-primary text-white shadow-md scale-110" : "bg-muted text-muted-foreground"}
  `}
>
```

Update the "browse" span to be more prominent:

```tsx
<span className="font-medium text-primary underline underline-offset-2 decoration-primary/30 hover:decoration-primary/60 transition-colors">browse</span>
```

**Step 3: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds.

**Step 4: Commit**

```bash
git add frontend/src/components/upload/
git commit -m "feat(frontend): polished upload dialog with glassmorphism, gradient buttons, and refined dropzone"
```

---

### Task 9: Polish the ErrorAlert and ConfirmDialog

**Files:**
- Modify: `frontend/src/components/shared/ErrorAlert.tsx`
- Modify: `frontend/src/components/shared/ConfirmDialog.tsx`

**Step 1: Update ErrorAlert with gradient border accent**

In `ErrorAlert.tsx`, update the Alert className:

```tsx
<Alert variant="destructive" className="animate-in slide-in-from-top-2 fade-in-0 duration-300 border-l-4 border-l-destructive shadow-sm">
```

**Step 2: Update ConfirmDialog with glass effect**

In `ConfirmDialog.tsx`, update AlertDialogContent:

```tsx
<AlertDialogContent className="glass border-white/20">
```

Update the destructive action button:

```tsx
<AlertDialogAction
  onClick={onConfirm}
  className={destructive ? "bg-destructive text-destructive-foreground shadow-sm shadow-destructive/20 hover:bg-destructive/90" : "gradient-primary border-0 hover:brightness-110"}
>
  {confirmLabel}
</AlertDialogAction>
```

**Step 3: Verify build**

Run: `cd frontend && npm run build`
Expected: Build succeeds.

**Step 4: Commit**

```bash
git add frontend/src/components/shared/
git commit -m "feat(frontend): refined error alerts with accent border and glassmorphism dialogs"
```

---

### Task 10: Visual review in browser and final adjustments

**Files:**
- Potentially modify any component file based on visual review findings

**Step 1: Start the dev server**

Run: `cd frontend && npm run dev`

**Step 2: Open browser and verify each view**

Check each screen visually:
1. Empty state (no document selected) — gradient icon, centered text
2. Upload dialog — glassmorphism, gradient button, dropzone interactions
3. Processing state — animated checkmarks, gradient progress, step highlighting
4. Editor — section cards with shadows, bullet active glow, citation animations
5. Sidebar — gradient logo, card hover lifts, active state gradient

**Step 3: Fix any visual issues found**

Address spacing inconsistencies, color mismatches, animation timing issues, or any broken styling.

**Step 4: Commit fixes**

```bash
git add -A frontend/src/
git commit -m "fix(frontend): visual polish adjustments from browser review"
```

---

### Task 11: Final build verification and gitignore cleanup

**Files:**
- Modify: `frontend/.gitignore` (if needed)

**Step 1: Run production build**

Run: `cd frontend && npm run build`
Expected: Build succeeds with no errors or warnings.

**Step 2: Ensure undesirable files are excluded**

Verify `.DS_Store`, `dist/`, `tsconfig.tsbuildinfo` are not tracked:

Run: `cd /Users/robert/Projects/SlideNode && git status`

If `.DS_Store` files or `dist/` appear in untracked, make sure `.gitignore` excludes them.

**Step 3: Stage and commit all remaining changes**

```bash
cd /Users/robert/Projects/SlideNode
git add frontend/
git commit -m "feat(frontend): complete frontend redesign with premium visual polish

- Modular component architecture (30+ components replacing 3 monolithic ones)
- Tailwind CSS + shadcn/ui design system with custom gradient theme
- Glassmorphism dialogs, animated pipeline progress, staggered section reveals
- Dual-pane editor with citation sync and inline editing
- Custom hooks for state management, job polling, draft tracking
- Responsive sidebar with document management"
```

---

### Task 12: Create PR to main

**Step 1: Push the branch**

Run: `git push -u origin feature/frontend-redesign`

**Step 2: Create PR**

```bash
gh pr create --title "Complete frontend redesign with premium visual polish" --body "$(cat <<'EOF'
## Summary
- Replaced monolithic frontend (3 components) with modular architecture (30+ focused components)
- Added Tailwind CSS + shadcn/ui + Radix UI design system
- Premium visual treatment: gradient accents, glassmorphism, animations, refined typography
- Custom hooks: useAppState, useJobPoller, useDeckDraft, useCitationSync
- Dual-pane editor with citation synchronization and inline editing

## Test plan
- [ ] `npm run build` passes cleanly
- [ ] Upload PDF flow works end-to-end
- [ ] Processing pipeline progress displays correctly
- [ ] Inline editing of all deck content works
- [ ] Citation pane syncs with bullet clicks
- [ ] Markdown and PPTX export work
- [ ] Document deletion with confirmation works
- [ ] Sidebar document switching works
- [ ] Visual polish is consistent across all views

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
