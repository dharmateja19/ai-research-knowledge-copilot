import { useRef, useEffect, useState } from "react";

function App() {
	const socketRef = useRef(null);

	const [question, setQuestion] = useState("");
	const [loading, setLoading] = useState(false);
	const [conversations, setConversations] = useState([]);
	const [conversationId, setConversationId] = useState(null);
	const [messages, setMessages] = useState([]);
	const [visibleSources, setVisibleSources] = useState({});
	const [documents, setDocuments] = useState([]);
	const [uploading, setUploading] = useState(false);
	const [conversationDocuments, setConversationDocuments] = useState([]);

	const askQuestion = () => {
		if (!question.trim() || loading || !conversationId) return;

		if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
			console.error("WebSocket is not connected");
			return;
		}

		const userQuestion = question;

		setLoading(true);

		setMessages((previous) => [
			...previous,
			{
				role: "user",
				content: userQuestion,
			},
			{
				role: "assistant",
				content: "",
				sources: [],
			},
		]);

		socketRef.current.send(
			JSON.stringify({
				conversation_id: conversationId,
				question: userQuestion,
			}),
		);

		setQuestion("");
	};
	const handleKeyDown = (event) => {
		if (event.key === "Enter") {
			askQuestion();
		}
	};

	const createConversation = async () => {
		try {
			const response = await fetch("http://127.0.0.1:8000/conversations", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					title: "New Chat",
				}),
			});

			const data = await response.json();

			setConversationId(data.id);

			setConversations((previous) => [...previous, data]);

			console.log("Conversation created:", data.id);
		} catch (error) {
			console.error("Failed to create conversation:", error);
		}
	};

	const loadConversations = async () => {
		try {
			const response = await fetch("http://127.0.0.1:8000/conversations");

			const data = await response.json();

			setConversations(data);

			if (data.length > 0) {
				setConversationId(data[0].id);
				loadMessages(data[0].id);
			}
		} catch (error) {
			console.error("Failed to load conversations:", error);
		}
	};

	const loadConversationDocuments = async (id) => {
		try {
			const response = await fetch(
				`http://127.0.0.1:8000/conversations/${id}/documents`,
			);

			if (!response.ok) {
				throw new Error("Failed to load conversation documents");
			}

			const data = await response.json();

			setConversationDocuments(data);
		} catch (error) {
			console.error("Error loading conversation documents:", error);
		}
	};

	const toggleDocument = async (documentId) => {
		const attached = conversationDocuments.some(
			(document) => document.id === documentId,
		);

		try {
			if (attached) {
				const response = await fetch(
					`http://127.0.0.1:8000/conversations/${conversationId}/documents/${documentId}`,
					{
						method: "DELETE",
					},
				);

				if (!response.ok) {
					throw new Error("Failed to detach document");
				}
			} else {
				const response = await fetch(
					`http://127.0.0.1:8000/conversations/${conversationId}/documents/${documentId}`,
					{
						method: "POST",
					},
				);

				if (!response.ok) {
					throw new Error("Failed to attach document");
				}
			}

			await loadConversationDocuments(conversationId);
		} catch (error) {
			console.error("Document toggle error:", error);
		}
	};

	const loadMessages = async (id) => {
		try {
			const response = await fetch(
				`http://127.0.0.1:8000/conversations/${id}/messages`,
			);

			const data = await response.json();

			setMessages(
				data.map((message) => ({
					role: message.role,
					content: message.content,
					sources: message.sources || [],
				})),
			);

			setVisibleSources({});
			setQuestion("");
			await loadConversationDocuments(id);
		} catch (error) {
			console.error("Failed to load messages:", error);
		}
	};

	const loadDocuments = async () => {
		try {
			const response = await fetch("http://127.0.0.1:8000/documents");

			if (!response.ok) {
				throw new Error("Failed to load documents");
			}

			const data = await response.json();
			setDocuments(data);
		} catch (error) {
			console.error("Error loading documents:", error);
		}
	};

	const uploadDocument = async (event) => {
		const file = event.target.files[0];

		if (!file) return;

		if (file.type !== "application/pdf") {
			alert("Please select a PDF file.");
			return;
		}

		const formData = new FormData();
		formData.append("file", file);

		try {
			setUploading(true);

			const response = await fetch("http://127.0.0.1:8000/documents/upload", {
				method: "POST",
				body: formData,
			});

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.detail || "Upload failed");
			}

			console.log("Uploaded:", data);

			await loadDocuments();
		} catch (error) {
			console.error("Upload error:", error);
			alert(error.message);
		} finally {
			setUploading(false);
			event.target.value = "";
		}
	};

	const deleteDocument = async (documentId) => {
		const confirmed = window.confirm(
			"Are you sure you want to delete this document?",
		);

		if (!confirmed) return;

		try {
			const response = await fetch(
				`http://127.0.0.1:8000/documents/${documentId}`,
				{
					method: "DELETE",
				},
			);

			const data = await response.json();

			if (!response.ok) {
				throw new Error(data.detail || "Delete failed");
			}

			console.log("Deleted:", data);

			await loadDocuments();
		} catch (error) {
			console.error("Delete error:", error);
			alert(error.message);
		}
	};

	useEffect(() => {
		const socket = new WebSocket("ws://127.0.0.1:8000/ws/chat");

		socketRef.current = socket;

		socket.onopen = () => {
			console.log("WebSocket connected");
		};

		socket.onmessage = (event) => {
			const data = JSON.parse(event.data);

			if (data.type === "sources") {
				setMessages((previous) => {
					const updated = [...previous];
					const lastMessage = updated[updated.length - 1];

					if (lastMessage?.role === "assistant") {
						updated[updated.length - 1] = {
							...lastMessage,
							sources: data.sources,
						};
					}

					return updated;
				});
			}

			if (data.type === "token") {
				setMessages((previous) => {
					const updated = [...previous];
					const lastMessage = updated[updated.length - 1];

					if (lastMessage?.role === "assistant") {
						updated[updated.length - 1] = {
							...lastMessage,
							content: lastMessage.content + data.content,
						};
					}

					return updated;
				});
			}

			if (data.type === "done") {
				setLoading(false);
			}
		};

		socket.onerror = (error) => {
			console.error("WebSocket error:", error);
			setLoading(false);
		};

		socket.onclose = () => {
			console.log("WebSocket disconnected");
		};

		return () => {
			socket.close();
			socketRef.current = null;
		};
	}, []);

	useEffect(() => {
		(loadConversations(), loadDocuments());
	}, []);

	return (
		<div className="min-h-screen bg-gray-950 text-white">
			<div className="flex h-screen">
				{/* Sidebar */}
				<aside className="w-64 border-r border-gray-800 bg-gray-900 p-4">
					<h1 className="text-xl font-bold">AI Research</h1>

					<p className="mt-1 text-sm text-gray-400">Knowledge Copilot</p>

					<button
						onClick={createConversation}
						className="w-full rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium hover:bg-gray-700"
					>
						+ New Chat
					</button>
					<div className="mt-4 space-y-2">
						{conversations.map((conversation) => (
							<button
								key={conversation.id}
								onClick={() => {
									setConversationId(conversation.id);
									loadMessages(conversation.id);
								}}
								className={`w-full rounded-lg px-3 py-2 text-left text-sm ${
									conversation.id === conversationId
										? "bg-gray-700 text-white font-medium"
										: "hover:bg-gray-700"
								}`}
							>
								{conversation.title}
							</button>
						))}
					</div>
					<div className="mt-8">
						<div className="flex items-center justify-between mb-3">
							<h2 className="text-sm font-semibold text-gray-400 uppercase">
								Documents
							</h2>

							<label
								className="text-gray-400 hover:text-white text-xl cursor-pointer"
								title="Upload PDF"
							>
								{uploading ? "..." : "+"}

								<input
									type="file"
									accept="application/pdf"
									onChange={uploadDocument}
									className="hidden"
									disabled={uploading}
								/>
							</label>
						</div>

						<div className="space-y-1">
							{documents.map((document) => {
								const attached = conversationDocuments.some(
									(item) => item.id === document.id,
								);

								return (
									<div
										key={document.id}
										className="flex items-center gap-2 px-3 py-2 rounded-lg text-gray-300 hover:bg-gray-700"
									>
										<input
											type="checkbox"
											checked={attached}
											onChange={() => toggleDocument(document.id)}
											disabled={!conversationId}
											className="accent-gray-400"
										/>

										{/* <span>📄</span> */}

										<span
											className="text-sm truncate flex-1"
											title={document.filename}
										>
											{document.filename}
										</span>

										<button
											onClick={() => deleteDocument(document.id)}
											className="text-gray-500 hover:text-red-400 text-sm"
											title="Delete document"
										>
											🗑️
										</button>
									</div>
								);
							})}
						</div>
					</div>
				</aside>

				{/* Main */}
				<main className="flex flex-1 flex-col">
					{/* Header */}
					<header className="border-b border-gray-800 px-6 py-4">
						<h2 className="text-lg font-semibold">Research Assistant</h2>

						<p className="text-sm text-gray-400">
							Ask questions about your research documents
						</p>
					</header>

					{/* Chat */}
					<div className="flex-1 overflow-y-auto p-6">
						<div className="mx-auto max-w-3xl">
							{/* Chat Messages */}
							<div className="space-y-6">
								{messages.map((message, index) => (
									<div key={index}>
										<div className="mb-2 text-sm font-semibold text-gray-400">
											{message.role === "user"
												? "You"
												: "AI Research Assistant"}
										</div>

										<div
											className={
												message.role === "user"
													? "rounded-xl bg-gray-800 p-4"
													: "rounded-xl border border-gray-800 bg-gray-900 p-5 whitespace-pre-wrap"
											}
										>
											{message.content}
										</div>

										{/* Sources */}
										{message.role === "assistant" &&
											message.sources?.length > 0 && (
												<div className="mt-2">
													<button
														onClick={() =>
															setVisibleSources((previous) => ({
																...previous,
																[index]: !previous[index],
															}))
														}
														className="text-sm text-gray-400 hover:text-white hover:underline"
													>
														{visibleSources[index]
															? "Hide sources"
															: "View sources"}
													</button>

													{visibleSources[index] && (
														<div className="mt-3 space-y-2">
															{message.sources.map((source) => (
																<div
																	key={source.chunk_id}
																	className="rounded-lg border border-gray-800 bg-gray-950 p-3"
																>
																	<p className="text-sm text-gray-300">
																		📄 {source.document}
																	</p>

																	<p className="mt-1 text-xs text-gray-500">
																		Page {source.page}
																	</p>
																</div>
															))}
														</div>
													)}
												</div>
											)}
									</div>
								))}
							</div>

							{/* Loading */}
							{loading && (
								<div className="text-sm text-gray-500">
									Researching your documents...
								</div>
							)}
						</div>
					</div>

					{/* Input */}
					<div className="border-t border-gray-800 p-4">
						<div className="mx-auto flex max-w-3xl gap-3">
							<input
								type="text"
								value={question}
								onChange={(event) => setQuestion(event.target.value)}
								onKeyDown={handleKeyDown}
								placeholder="Ask a research question..."
								disabled={loading}
								className="flex-1 rounded-xl border border-gray-700 bg-gray-900 px-4 py-3 text-white outline-none placeholder:text-gray-500 focus:border-gray-500 disabled:opacity-50"
							/>

							<button
								onClick={askQuestion}
								disabled={loading || !question.trim()}
								className="rounded-xl bg-white px-5 py-3 font-medium text-gray-900 hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
							>
								{loading ? "..." : "Send"}
							</button>
						</div>
					</div>
				</main>
			</div>
		</div>
	);
}

export default App;
