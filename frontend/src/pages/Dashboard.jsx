import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

import { Plus, Trash2, LogOut, Users, ShieldCheck, Camera, Activity, Search, ShieldAlert, AlertCircle } from 'lucide-react';

export default function Dashboard() {
    const { logout, user } = useAuth();
    const [staff, setStaff] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');

    // Form State
    const [formData, setFormData] = useState({
        staff_id: '',
        name: '',
        role: 'Employee'
    });
    const [images, setImages] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchStaff();
    }, []);

    const fetchStaff = async () => {
        try {
            const res = await api.get('/staff/');
            setStaff(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm("Are you sure you want to terminate this identity?")) return;
        try {
            await api.delete(`/staff/${id}`);
            fetchStaff();
        } catch (err) {
            console.error(err);
        }
    };

    const handleEnroll = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const data = new FormData();
            data.append('staff_id', formData.staff_id);
            data.append('name', formData.name);
            data.append('role', formData.role);
            for (let i = 0; i < images.length; i++) {
                data.append('images', images[i]);
            }

            await api.post('/staff/enroll', data);
            setShowModal(false);
            setFormData({ staff_id: '', name: '', role: 'Employee' });
            setImages([]);
            fetchStaff();
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const filteredStaff = staff.filter(s =>
        s.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.staff_id.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="min-h-screen bg-slate-950 text-slate-100 flex overflow-hidden">
            {/* Sidebar */}
            <aside className="w-72 glass-morphism border-r border-white/5 flex flex-col z-30">
                <div className="p-8">
                    <div className="flex items-center gap-3 mb-10">
                        <div className="w-10 h-10 bg-blue-500/20 rounded-xl flex items-center justify-center border border-blue-500/30">
                            <ShieldCheck className="w-6 h-6 text-blue-400" />
                        </div>
                        <h1 className="text-xl font-bold tracking-tight">Sentinel Admin</h1>
                    </div>

                    <nav className="space-y-2">
                        <Link to="/" className="flex items-center gap-3 px-4 py-3 bg-blue-600/10 text-blue-400 rounded-xl font-medium border border-blue-600/20">
                            <Users className="w-5 h-5" /> Staff Management
                        </Link>
                        <Link to="/recognize" className="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-white hover:bg-white/5 rounded-xl transition-all font-medium">
                            <Camera className="w-5 h-5" /> Kiosk Mode
                        </Link>
                    </nav>
                </div>

                <div className="mt-auto p-8 border-t border-white/5">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center border border-white/10 uppercase font-bold text-xs">
                            {user?.username?.charAt(0) || 'A'}
                        </div>
                        <div className="overflow-hidden">
                            <p className="text-sm font-semibold truncate">{user?.username || 'Administrator'}</p>
                            <p className="text-xs text-slate-500 font-medium capitalize">Root Access</p>
                        </div>
                    </div>
                    <button onClick={logout} className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded-xl transition-all font-semibold">
                        <LogOut className="w-5 h-5" /> Logout Session
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto bg-[radial-gradient(at_top_right,rgba(30,41,59,1)_0%,rgba(15,23,42,1)_100%)] p-8 lg:p-12 relative">
                {/* Header Stats */}
                {/* <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                    <div className="glass-card p-6 border-white/5 hover:border-blue-500/30 transition-all group">
                        <div className="flex items-center justify-between mb-4">
                            <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400 group-hover:scale-110 transition-transform">
                                <Users className="w-6 h-6" />
                            </div>
                            <span className="text-xs font-bold text-blue-400/50 uppercase tracking-widest">Database</span>
                        </div>
                        <p className="text-3xl font-bold">{staff.length}</p>
                        <p className="text-sm text-slate-400 font-medium">Total Enrolled Identities</p>
                    </div>

                    <div className="glass-card p-6 border-white/5 hover:border-green-500/30 transition-all group">
                        <div className="flex items-center justify-between mb-4">
                            <div className="p-3 bg-green-500/10 rounded-xl text-green-400 group-hover:scale-110 transition-transform">
                                <Activity className="w-6 h-6" />
                            </div>
                            <span className="text-xs font-bold text-green-400/50 uppercase tracking-widest">Status</span>
                        </div>
                        <p className="text-3xl font-bold">{staff.filter(s => s.status === 'active').length}</p>
                        <p className="text-sm text-slate-400 font-medium">Verified Active Subjects</p>
                    </div>

                    <div className="glass-card p-6 border-white/5 hover:border-amber-500/30 transition-all group">
                        <div className="flex items-center justify-between mb-4">
                            <div className="p-3 bg-amber-500/10 rounded-xl text-amber-400 group-hover:scale-110 transition-transform">
                                <ShieldAlert className="w-6 h-6" />
                            </div>
                            <span className="text-xs font-bold text-amber-400/50 uppercase tracking-widest">Network</span>
                        </div>
                        <p className="text-3xl font-bold">Operational</p>
                        <p className="text-sm text-slate-400 font-medium">Edge Computing Nodes Live</p>
                    </div>
                </div> */}

                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8">
                    <div>
                        <h2 className="text-3xl font-bold tracking-tight">Identities</h2>
                        <p className="text-slate-400 mt-1 font-medium">Manage and monitor verified personnel</p>
                    </div>

                    <div className="flex items-center gap-3 w-full md:w-auto">
                        <div className="relative flex-1 md:w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                            <input
                                type="text"
                                placeholder="Search hash or name..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                            />
                        </div>
                        <button
                            onClick={() => setShowModal(true)}
                            className="bg-blue-600 hover:bg-blue-500 text-white px-5 py-2.5 rounded-xl flex items-center gap-2 transition-all font-bold shadow-lg shadow-blue-900/40 active:scale-95 text-sm whitespace-nowrap"
                        >
                            <Plus className="w-4 h-4" /> Enroll Profile
                        </button>
                    </div>
                </div>

                {/* Staff Table */}
                <div className="glass-card border-white/5 overflow-hidden shadow-2xl">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="bg-white/5 border-b border-white/5">
                                    <th className="px-6 py-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Identification Hash</th>
                                    <th className="px-6 py-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Subject Name</th>
                                    <th className="px-6 py-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Classification</th>
                                    <th className="px-6 py-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Status</th>
                                    <th className="px-6 py-5 text-xs font-bold text-slate-500 uppercase tracking-widest">Operations</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {filteredStaff.map((s) => (
                                    <tr key={s.id} className="hover:bg-white/[0.02] transition-colors group">
                                        <td className="px-6 py-5 font-mono text-sm text-blue-400/80 group-hover:text-blue-400 transition-colors">
                                            {s.staff_id}
                                        </td>
                                        <td className="px-6 py-5 font-bold tracking-tight text-slate-200">
                                            {s.name}
                                        </td>
                                        <td className="px-6 py-5">
                                            <span className="px-3 py-1 bg-slate-800 text-slate-300 rounded-full text-[10px] font-bold uppercase tracking-wider border border-white/5">
                                                {s.role}
                                            </span>
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex items-center gap-2">
                                                <div className={`w-1.5 h-1.5 rounded-full ${s.status === 'active' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]' : 'bg-red-500 active:scale-95'}`}></div>
                                                <span className={`text-xs font-bold capitalize ${s.status === 'active' ? 'text-green-400' : 'text-red-400'}`}>
                                                    {s.status}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <button
                                                onClick={() => handleDelete(s.staff_id)}
                                                className="text-slate-500 hover:text-red-400 transition-colors"
                                                title="Revoke Access"
                                            >
                                                <Trash2 className="w-5 h-5" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                                {filteredStaff.length === 0 && (
                                    <tr>
                                        <td colSpan="5" className="px-6 py-12 text-center text-slate-500 font-medium">
                                            {searchQuery ? "No matches found in security database." : "Security database is currently empty."}
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>

            {/* Enroll Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center z-[60] p-4">
                    <div className="glass-card p-8 w-full max-w-xl border-white/10 shadow-3xl bg-slate-900/50">
                        <div className="flex items-center justify-between mb-8">
                            <div>
                                <h3 className="text-2xl font-bold">Identity Enrollment</h3>
                                <p className="text-slate-400 text-sm font-medium mt-1">Initialize biometric and profile data</p>
                            </div>
                            <button onClick={() => setShowModal(false)} className="text-slate-500 hover:text-white transition-colors">
                                <Plus className="w-6 h-6 rotate-45" />
                            </button>
                        </div>

                        <form onSubmit={handleEnroll} className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-slate-400 ml-1 uppercase tracking-widest">Internal ID</label>
                                    <input required type="text" className="input-field bg-white/5 h-12"
                                        placeholder="EMP-001"
                                        value={formData.staff_id} onChange={e => setFormData({ ...formData, staff_id: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-slate-400 ml-1 uppercase tracking-widest">Classification</label>
                                    <select className="input-field bg-white/5 h-12"
                                        value={formData.role} onChange={e => setFormData({ ...formData, role: e.target.value })}
                                    >
                                        <option value="Employee">Employee</option>
                                        <option value="Security">Security</option>
                                        <option value="Admin">Admin</option>
                                        <option value="Manager">Manager</option>
                                    </select>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-bold text-slate-400 ml-1 uppercase tracking-widest">Official Designation</label>
                                <input required type="text" className="input-field bg-white/5 h-12"
                                    placeholder="Full Legal Name"
                                    value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>

                            <div className="space-y-4">
                                <label className="text-xs font-bold text-slate-400 ml-1 uppercase tracking-widest">Biometric Sampling (9-Point Precision Encoding)</label>
                                <div className="grid grid-cols-1 gap-4">
                                    <div className="relative group">
                                        <input required type="file" multiple accept="image/*" className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                                            onChange={e => setImages(e.target.files)}
                                        />
                                        <div className="input-field min-h-[160px] flex flex-col items-center justify-center p-6 gap-4 border-dashed border-2 bg-blue-500/5 border-blue-500/20 group-hover:bg-blue-500/10 group-hover:border-blue-500/40 transition-all">
                                            <div className="grid grid-cols-3 gap-2 opacity-50 group-hover:opacity-100 transition-opacity">
                                                {[
                                                    'TILT LEFT', 'UP', 'TILT RIGHT',
                                                    'LEFT 90°', 'FRONT', 'RIGHT 90°',
                                                    'LEFT 45°', 'DOWN', 'RIGHT 45°'
                                                ].map(pose => (
                                                    <div key={pose} className="w-16 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-[7px] font-black text-center px-1 leading-tight border border-white/5">
                                                        {pose}
                                                    </div>
                                                ))}
                                            </div>
                                            <div className="text-center">
                                                <span className="text-xs font-bold text-blue-400 block mb-1">
                                                    {images.length > 0 ? `${images.length} Secure Fragments Selected` : "Drop 9-Angle Sample Batch"}
                                                </span>
                                                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Supports Multi-Upload (Front, Sides, Tilted, Up/Down)</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-xl flex items-start gap-4">
                                        <ShieldCheck className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                                        <div className="space-y-1">
                                            <p className="text-[10px] text-blue-200 font-black uppercase tracking-widest">Performance Protocol</p>
                                            <p className="text-[10px] text-blue-200/60 font-medium leading-relaxed uppercase">
                                                For "Zero Failure" recognition, upload 9 photos covering all head rotations. This creates a full 180° biometric spatial map.
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex gap-4 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="flex-1 h-12 rounded-xl text-slate-400 font-bold hover:bg-white/5 transition-colors border border-transparent hover:border-white/5"
                                >
                                    Abort
                                </button>
                                <button
                                    disabled={loading || images.length === 0}
                                    type="submit"
                                    className="flex-1 h-12 bg-blue-600 hover:bg-blue-500 rounded-xl text-white font-bold disabled:opacity-50 transition-all shadow-lg shadow-blue-900/40 active:scale-95"
                                >
                                    {loading ? (
                                        <div className="flex items-center justify-center gap-2">
                                            <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                            Encoding...
                                        </div>
                                    ) : 'Verify & Enroll'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
