# Frontend Workflow

## Adding a New Feature

1. **API Integration**
   - Update `src/services/api/index.ts` with new endpoints
   - Create/Update React Query hooks in `src/hooks/`

2. **Create Components**
   - Build reusable components in `src/components/`
   - Use Tailwind CSS for styling

3. **Create Page**
   - Assemble components in `src/pages/`
   - Add route in `src/App.tsx`

4. **State Management**
   - Use React Query for server state
   - Use Context/Zustand for complex local state (if needed)

5. **Update Documentation**
   - Update `docs/code_reference.md`
