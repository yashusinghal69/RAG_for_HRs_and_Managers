"use client";

import * as React from "react";
import { Plus, Building2, MessageSquare, Trash2 } from "lucide-react";
import { useLocalStorage } from "@/hooks/use-local-storage";

import { NavUser } from "@/components/nav-user";
import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenuAction,
} from "@/components/ui/sidebar";

interface ChatSession {
  id: string;
  title: string;
  isActive: boolean;
}

// Sample chat sessions data - start with empty array
const data = {
  user: {
    name: "HR Assistant",
    email: "hr@novacorp.com",
    avatar: "/avatars/hr-avatar.jpg",
  },
  company: {
    name: "NovaCorp",
    logo: Building2,
    department: "HR Department",
  },
  chatSessions: [] as ChatSession[], // Start with no pre-loaded chats
};

export function AppSidebar({
  currentUserRole,
  activeChat,
  onChatSelect,
  onNewChat,
  onAddChatSession,
  ...props
}: React.ComponentProps<typeof Sidebar> & {
  currentUserRole?: string;
  activeChat?: string;
  onChatSelect?: (chatId: string) => void;
  onNewChat?: () => void;
  onAddChatSession?: (addFunction: (title: string) => string) => void;
}) {
  const [chatSessions, setChatSessions, isLoadingChats] = useLocalStorage<
    ChatSession[]
  >("hr-chat-sessions", data.chatSessions);

  const handleNewChat = () => {
    // Set all existing chats to inactive
    setChatSessions((prev) =>
      prev.map((chat) => ({ ...chat, isActive: false }))
    );
    // Call the parent component's new chat handler
    onNewChat?.();
    console.log("New chat clicked - clearing active chats");
  };

  const handleDeleteChat = (chatId: string) => {
    setChatSessions((prev) => {
      const filtered = prev.filter((chat) => chat.id !== chatId);
      // If we deleted the active chat and there are other chats, make the first one active
      if (
        prev.find((chat) => chat.id === chatId)?.isActive &&
        filtered.length > 0
      ) {
        filtered[0].isActive = true;
        onChatSelect?.(filtered[0].id);
      } else if (filtered.length === 0) {
        // If no chats left, trigger new chat
        onNewChat?.();
      }
      return filtered;
    });
  };

  const handleSelectChat = (chatId: string) => {
    setChatSessions((prev) =>
      prev.map((chat) => ({
        ...chat,
        isActive: chat.id === chatId,
      }))
    );
    onChatSelect?.(chatId);
  };

  // Function to add a new chat session
  const addChatSession = React.useCallback((title: string) => {
    const newChat = {
      id: String(Date.now()),
      title: title.length > 30 ? title.substring(0, 30) + "..." : title,
      isActive: true,
    };

    setChatSessions((prev) => [
      newChat,
      ...prev.map((chat) => ({ ...chat, isActive: false })),
    ]);

    return newChat.id;
  }, []);

  // Provide the addChatSession function to parent component
  React.useEffect(() => {
    onAddChatSession?.(addChatSession);
  }, [addChatSession, onAddChatSession]);

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader className="border-b">
        {/* Company Header */}
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" className="cursor-default">
              <div className="bg-primary text-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                <data.company.logo className="size-4" />
              </div>
              <div className="grid flex-1 text-left text-sm leading-tight">
                <span className="truncate font-semibold">
                  {data.company.name}
                </span>
                <span className="truncate text-xs text-muted-foreground">
                  {data.company.department}
                </span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        {/* Chat Sessions */}
        <SidebarGroup>
          <SidebarGroupLabel>Conversations</SidebarGroupLabel>
          <SidebarMenu suppressHydrationWarning>
            {/* New Chat Button */}
            <SidebarMenuItem>
              <SidebarMenuButton
                onClick={handleNewChat}
                className="justify-start gap-2"
              >
                <Plus className="size-4" />
                <span>New Chat</span>
              </SidebarMenuButton>
            </SidebarMenuItem>

            {/* Chat Sessions List - Only render when not loading to avoid hydration issues */}
            {!isLoadingChats &&
              chatSessions.map((chat) => (
                <SidebarMenuItem key={chat.id}>
                  <SidebarMenuButton
                    onClick={() => handleSelectChat(chat.id)}
                    isActive={chat.isActive}
                    className="justify-start gap-2"
                  >
                    <MessageSquare className="size-4" />
                    <span className="truncate">{chat.title}</span>
                  </SidebarMenuButton>
                  <SidebarMenuAction
                    onClick={() => handleDeleteChat(chat.id)}
                    className="opacity-0 group-hover/menu-item:opacity-100"
                  >
                    <Trash2 className="size-4" />
                    <span className="sr-only">Delete chat</span>
                  </SidebarMenuAction>
                </SidebarMenuItem>
              ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
