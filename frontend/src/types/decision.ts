export type Decision = {
  id: string; organization_id: string | null; user_id: string; model_id: string;
  model_name: string | null; title: string | null; category: string;
  prompt_hash: string; recommendation_text: string; diff_content: string | null;
  affected_files: string[]; status: string; created_at: string;
  prev_hash: string | null; row_hash: string;
}
export type DecisionPage = { items: Decision[]; page: number; page_size: number; total: number }
export type Catalog = { users: { id: string; email: string }[]; models: { id: string; provider: string; name: string; version: string | null }[] }
export type DecisionCreate = { user_id: string; model_id: string; title: string; prompt?: string; recommendation_text: string; diff_content: string; category: string; affected_files: string[] }
