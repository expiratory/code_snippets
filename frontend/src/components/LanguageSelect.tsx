import React, { useCallback } from 'react';
import AsyncCreatableSelect from 'react-select/async-creatable';
import { Filter, Check } from 'lucide-react';
import { components, type OptionProps } from 'react-select';
import { useTranslation } from 'react-i18next';
import api from '../lib/api';

interface Language {
  id: number;
  name: string;
  slug: string;
}

interface LanguageSelectProps {
  value: Language | null;
  onChange: (value: Language | null) => void;
  className?: string;
  variant?: 'default' | 'filter';
}

function debounce<T extends (...args: any[]) => any>(func: T, wait: number) {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

const CustomOption = (props: OptionProps<any>) => {
  return (
    <components.Option {...props}>
      <div className="flex items-center justify-between w-full">
        <span>{props.label}</span>
        {props.isSelected && <Check className="w-4 h-4" />}
      </div>
    </components.Option>
  );
};

export const LanguageSelect: React.FC<LanguageSelectProps> = ({
  value,
  onChange,
  className,
  variant = 'default'
}) => {
  const { t } = useTranslation();
  const [selectKey, setSelectKey] = React.useState(0);

  const loadOptions = (inputValue: string, callback: (options: any[]) => void) => {
    api.get<Language[]>('/languages', {
      params: { query: inputValue, limit: 20 }
    }).then(response => {
      const options: { label: string; value: Language | null }[] = response.data.map(lang => ({
        label: lang.name,
        value: lang
      }));
      if (variant === 'filter' && !inputValue) {
        options.unshift({ label: t('snippets.languages.all'), value: null });
      }
      callback(options);
    }).catch(error => {
      console.error('Failed to load languages:', error);
      callback([]);
    });
  };

  const debouncedLoadOptions = useCallback(debounce(loadOptions, 300), [t]);

  const handleCreate = async (inputValue: string) => {
    const trimmedInput = inputValue.trim();
    if (!trimmedInput) return;

    try {
      const response = await api.post<Language>('/languages', { name: trimmedInput });
      const newLanguage = response.data;
      onChange(newLanguage);
      setSelectKey(prev => prev + 1);
    } catch (error) {
      console.error('Failed to create language:', error);
    }
  };

  const handleChange = (option: any) => {
    onChange(option ? option.value : null);
  };

  const baseControlStyles = "!rounded-xl transition-all";
  const defaultControlStyles = "!bg-gray-50 dark:!bg-[#0f0f11] !border !border-gray-200 dark:!border-dark-border !min-h-[48px] !shadow-none";
  const filterControlStyles = "!bg-white dark:!bg-dark-surface !border !border-gray-200 dark:!border-dark-border !shadow-sm !min-h-[56px] !pl-12";

  return (
    <div className="relative">
      {variant === 'filter' && (
        <Filter className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 z-10 pointer-events-none" />
      )}
      <AsyncCreatableSelect
        key={selectKey}
        cacheOptions
        defaultOptions
        loadOptions={debouncedLoadOptions}
        onCreateOption={handleCreate}
        onChange={handleChange}
        value={value ? { label: value.name, value: value } : (variant === 'filter' ? { label: t('snippets.languages.all'), value: null } : null)}
        className={className}
        isValidNewOption={(inputValue) => variant !== 'filter' && inputValue.trim().length > 0}
        getOptionValue={(option: any) => typeof option.value === 'object' && option.value?.id ? option.value.id.toString() : option.label}
        components={{
          Option: CustomOption,
          IndicatorSeparator: () => null
        }}
        classNames={{
          control: (state: { isFocused: boolean }) =>
            `${baseControlStyles} ${variant === 'filter' ? filterControlStyles : defaultControlStyles} ${
              state.isFocused
                ? '!border-primary-500 !ring-2 !ring-primary-500/50 !outline-none'
                : ''
            }`,
          input: () => '!text-gray-900 dark:!text-white',
          singleValue: () => '!text-gray-900 dark:!text-white',
          menu: () => '!bg-white dark:!bg-dark-surface !border !border-gray-200 dark:!border-dark-border !rounded-xl !shadow-xl !mt-2 !overflow-hidden !z-50',
          option: (state: { isFocused: boolean; isSelected: boolean }) =>
            `!cursor-pointer !px-4 !py-2 !flex !items-center !justify-between transition-colors hover:!bg-gray-50 dark:hover:!bg-dark-border ${
              state.isSelected
                ? '!text-primary-600 dark:!text-primary-400 !bg-primary-50 dark:!bg-primary-900/20'
                : state.isFocused
                  ? '!bg-gray-50 dark:!bg-dark-border !text-gray-700 dark:!text-gray-300'
                  : '!bg-transparent !text-gray-700 dark:!text-gray-300'
            }`,
          placeholder: () => '!text-gray-900 dark:!text-white whitespace-nowrap',
          valueContainer: () => variant === 'filter' ? '!pl-0' : '',
        }}
        placeholder={variant === 'filter' ? t('snippets.languages.all') : t('snippets.languages.select_placeholder')}
      />
    </div>
  );
};
