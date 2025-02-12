import React, { useState } from 'react';
import { Editor } from '@monaco-editor/react';

const CodeEditor: React.FC<{
  value: string;
  onChange: (value: string | undefined) => void;
  language: string;
  readOnly: boolean;
}> = ({ value, onChange, language, readOnly }) => {
  const handleEditorChange = (value: string | undefined) => {
    onChange(value);
  };

  return (
    <Editor
      defaultLanguage={language}
      value={value}
      onChange={readOnly ? undefined : handleEditorChange}
      theme="vs-dark"
      options={{
        minimap: { enabled: false },
        fontSize: 13,
        lineNumbers: "on",
        roundedSelection: false,
        scrollBeyondLastLine: false,
        automaticLayout: true,
        wordWrap: "on",
        readOnly: readOnly,
        domReadOnly: readOnly,
        theme: "vs-dark",
        backgroundColor: "rgb(24, 24, 24)",
      }}
    />
  );
};

export default CodeEditor; 