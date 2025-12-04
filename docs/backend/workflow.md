# Backend Workflow

## Adding a New Feature

1. **Define Model**
   - Create/Update Pydantic models in `app/schemas/`
   - (Future) Create SQLModel in `app/models/`

2. **Implement Service**
   - Add business logic in `app/services/`
   - Keep services pure and testable

3. **Create API Endpoint**
   - Add route in `app/api/`
   - Use dependency injection for services
   - Validate inputs using Schemas

4. **Register Route**
   - Add router to `app/main.py`

5. **Update Documentation**
   - Update `docs/api.md`
   - Update `docs/code_reference.md`

## Database Migrations (Planned)
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```
