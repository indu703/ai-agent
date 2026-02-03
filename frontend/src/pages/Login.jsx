import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Lock, User, ShieldCheck } from 'lucide-react';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { login } = useAuth();
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setError('');
        try {
            const success = await login(username, password);
            if (!success) {
                setError('Invalid administrative credentials');
            }
        } catch (err) {
            setError('System authentication error');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-slate-950">
            {/* Background Image with Overlay */}
            <div
                className="absolute inset-0 z-0 bg-cover bg-center opacity-40 scale-105"
                style={{ backgroundImage: "url('/login-bg.png')" }}
            />
            <div className="absolute inset-0 z-10 bg-gradient-to-br from-slate-950/80 via-transparent to-slate-950/80" />

            {/* Animated Glows */}
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-[120px] animate-pulse" />
            <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[120px] animate-pulse delay-1000" />

            <div className="relative z-20 w-full max-w-md px-4">
                <div className="glass-card shadow-2xl p-8 backdrop-blur-xl border-white/10">
                    <div className="flex flex-col items-center mb-10">
                        <div className="w-16 h-16 bg-blue-500/20 rounded-2xl flex items-center justify-center border border-blue-500/30 mb-4">
                            <ShieldCheck className="w-10 h-10 text-blue-400" />
                        </div>
                        <h2 className="text-3xl font-bold text-white tracking-tight">AI Agent Sentinel</h2>
                        <p className="text-slate-400 mt-2 font-medium">Administrative Access Protocol</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-slate-300 ml-1">Identity</label>
                            <div className="relative group">
                                <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-5 h-5 group-focus-within:text-blue-400 transition-colors" />
                                <input
                                    type="text"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    className="input-field pl-12 h-12 bg-white/5 border-white/10 group-hover:border-white/20 transition-all font-medium"
                                    placeholder="Enter username"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-semibold text-slate-300 ml-1">Passkey</label>
                            <div className="relative group">
                                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 w-5 h-5 group-focus-within:text-blue-400 transition-colors" />
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="input-field pl-12 h-12 bg-white/5 border-white/10 group-hover:border-white/20 transition-all font-medium"
                                    placeholder="••••••••"
                                    required
                                />
                            </div>
                        </div>

                        {error && (
                            <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-sm px-4 py-3 rounded-lg flex items-center gap-2">
                                <div className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" />
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className={`w-full h-12 relative overflow-hidden rounded-lg font-bold text-white transition-all transform active:scale-95 ${isSubmitting ? 'bg-blue-600/50 cursor-wait' : 'bg-blue-600 hover:bg-blue-500 shadow-lg shadow-blue-900/40'
                                }`}
                        >
                            {isSubmitting ? (
                                <div className="flex items-center justify-center gap-3">
                                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                    Authenticating...
                                </div>
                            ) : (
                                "Initialize Session"
                            )}
                        </button>
                    </form>

                    <div className="mt-10 pt-6 border-t border-white/5 text-center">
                        <p className="text-slate-500 text-sm">
                            &copy; 2026 Deepmind Sentinel. All systems operational.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
