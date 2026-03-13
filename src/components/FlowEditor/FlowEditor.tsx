import React, { useEffect, useRef } from 'react';
import { FreeLayoutEditor } from '@flowgram.ai/free-layout-editor';
import '@flowgram.ai/free-layout-editor/index.css';
import './FlowEditor.css';

const FlowEditor: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<any>(null);

  useEffect(() => {
    if (containerRef.current && !editorRef.current) {
      // Initialize Flowgram.ai Free Layout Editor
      const editor = new FreeLayoutEditor({
        container: containerRef.current,
        // Initial data matching our deer-flow nodes
        initialData: {
          nodes: [
            { id: 'supervisor', type: 'default', position: { x: 400, y: 100 }, data: { label: 'Supervisor' } },
            { id: 'researcher', type: 'default', position: { x: 200, y: 300 }, data: { label: 'Researcher' } },
            { id: 'analyst', type: 'default', position: { x: 600, y: 300 }, data: { label: 'Analyst' } },
          ],
          edges: [
            { id: 'e1', source: 'supervisor', target: 'researcher' },
            { id: 'e2', source: 'researcher', target: 'supervisor' },
            { id: 'e3', source: 'supervisor', target: 'analyst' },
            { id: 'e4', source: 'analyst', target: 'supervisor' },
          ],
        },
      });

      editorRef.current = editor;
    }

    return () => {
      if (editorRef.current) {
        editorRef.current.dispose();
        editorRef.current = null;
      }
    };
  }, []);

  return (
    <div className="flow-editor-wrapper">
      <div className="flow-editor-header">
        <h2 className="text-xl font-bold text-cyan-400">Agentic Orchestration Graph</h2>
        <span className="text-sm text-gray-400">Silicon DNA Handshake: Active</span>
      </div>
      <div ref={containerRef} className="flow-editor-container" />
    </div>
  );
};

export default FlowEditor;
