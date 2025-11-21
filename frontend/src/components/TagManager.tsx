import React, { useEffect, useState } from 'react';
import { Trash2, Tag as TagIcon } from 'lucide-react';
import api from '../lib/api';
import Modal from './Modal';

interface TagWithStats {
  id: number;
  name: string;
  snippet_count: number;
}

export const TagManager: React.FC = () => {
  const [tags, setTags] = useState<TagWithStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [tagToDelete, setTagToDelete] = useState<{ id: number; name: string } | null>(null);

  useEffect(() => {
    fetchTags();
  }, []);

  const fetchTags = async () => {
    try {
      const response = await api.get('/tags', { params: { with_stats: true } });
      setTags(response.data);
    } catch (err) {
      setError('Failed to load tags');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClick = (tagId: number, tagName: string) => {
    setTagToDelete({ id: tagId, name: tagName });
    setDeleteModalOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!tagToDelete) return;

    try {
      await api.delete(`/tags/${tagToDelete.id}`);
      setTags(tags.filter(t => t.id !== tagToDelete.id));
      setDeleteModalOpen(false);
      setTagToDelete(null);
    } catch (err) {
      setError('Failed to delete tag');
      console.error(err);
      setDeleteModalOpen(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="text-gray-500 dark:text-gray-400">Loading tags...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <div className="bg-white dark:bg-dark-surface rounded-2xl border border-gray-200 dark:border-dark-border p-8 shadow-xl dark:shadow-none">
        <div className="flex items-center gap-3 mb-8">
          <TagIcon className="w-8 h-8 text-primary-600 dark:text-primary-400" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Manage Tags
          </h1>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl text-red-600 dark:text-red-400">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tags.map(tag => (
            <div
              key={tag.id}
              className="flex items-center justify-between p-4 bg-gray-50 dark:bg-dark-bg rounded-xl border border-gray-200 dark:border-dark-border group hover:border-primary-200 dark:hover:border-primary-800 transition-colors"
            >
              <div>
                <span className="font-medium text-gray-900 dark:text-white block">
                  {tag.name}
                </span>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {tag.snippet_count} snippet{tag.snippet_count !== 1 ? 's' : ''}
                </span>
              </div>

              <button
                onClick={() => handleDeleteClick(tag.id, tag.name)}
                className="p-2 text-gray-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all opacity-0 group-hover:opacity-100 focus:opacity-100"
                title="Delete tag"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          ))}

          {tags.length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
              No tags found. Create some snippets to get started!
            </div>
          )}
        </div>
      </div>

      <Modal
        isOpen={deleteModalOpen}
        onClose={() => setDeleteModalOpen(false)}
        title="Delete Tag"
      >
        <div className="space-y-6">
          <p className="text-gray-600 dark:text-gray-300">
            Are you sure you want to delete the tag <span className="font-semibold text-gray-900 dark:text-white">"{tagToDelete?.name}"</span>?
            This will remove the tag from all associated snippets.
          </p>
          <div className="flex justify-end gap-3">
            <button
              onClick={() => setDeleteModalOpen(false)}
              className="px-4 py-2 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              onClick={handleConfirmDelete}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-medium shadow-sm"
            >
              Delete Tag
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
