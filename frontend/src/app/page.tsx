"use client";

import * as React from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { ModeToggle } from "@/components/mode-toggle";
import { RoleSelector, UserRole } from "@/components/role-selector";
import { HRChatDashboard } from "@/components/hr-chat-dashboard";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

export default function Home() {
  const [selectedRole, setSelectedRole] = React.useState<UserRole>("employee");
  const [activeChat, setActiveChat] = React.useState<string>("new");
  const addChatFunctionRef = React.useRef<((title: string) => string) | null>(
    null
  );

  const handleNewChat = React.useCallback(() => {
    console.log("New chat handler called - setting active chat to 'new'");
    setActiveChat("new");
  }, []);

  const handleChatSelect = React.useCallback((chatId: string) => {
    console.log("Chat selected:", chatId);
    setActiveChat(chatId);
  }, []);

  const handleAddChatSession = React.useCallback(
    (addFunction: (title: string) => string) => {
      // Store the add function from sidebar
      addChatFunctionRef.current = addFunction;
    },
    []
  );

  const handleChatCreated = React.useCallback((title: string) => {
    // When dashboard creates a chat, use the sidebar's add function
    if (addChatFunctionRef.current) {
      const newChatId = addChatFunctionRef.current(title);
      setActiveChat(newChatId);
      console.log("Chat created and set as active:", newChatId);
      return newChatId;
    }
    return null;
  }, []);

  return (
    <SidebarProvider>
      <AppSidebar
        currentUserRole={selectedRole}
        activeChat={activeChat}
        onChatSelect={handleChatSelect}
        onNewChat={handleNewChat}
        onAddChatSession={handleAddChatSession}
      />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator
              orientation="vertical"
              className="mr-2 data-[orientation=vertical]:h-4"
            />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem className="hidden md:block">
                  <BreadcrumbLink href="#">
                    NovaCorp HR Assistant
                  </BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>Chat</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
          <div className="ml-auto flex items-center gap-2 px-4">
            <RoleSelector
              selectedRole={selectedRole}
              onRoleChange={setSelectedRole}
            />
            <ModeToggle />
          </div>
        </header>

        {/* Main Chat Dashboard */}
        <div className="flex-1 h-[calc(100vh-4rem)]">
          <HRChatDashboard
            userRole={selectedRole}
            activeChat={activeChat}
            onChatCreated={handleChatCreated}
            isNewChat={activeChat === "new"}
          />
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
