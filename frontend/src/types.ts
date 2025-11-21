export interface Tag {
  id: number;
  name: string;
}

export interface Language {
  id: number;
  name: string;
  slug: string;
}

export interface Snippet {
  id: number;
  title: string;
  code: string;
  language: Language | string;
  tags?: Tag[];
}

export interface SnippetCreate {
  title: string;
  code: string;
  language: string;
}

export interface SnippetUpdate {
  title: string;
  code: string;
  language: string;
}
