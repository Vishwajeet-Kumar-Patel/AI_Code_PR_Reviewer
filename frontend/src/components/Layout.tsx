import { ReactNode } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

interface LayoutProps {
  children: ReactNode;
  user?: {
    name: string;
    avatar_url?: string;
  };
}

export default function Layout({ children, user }: LayoutProps) {
  return (
    <div className="flex h-screen bg-dark-900 text-white">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header user={user} />
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
