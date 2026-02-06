import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
    faChartLine,
    faPlus,
    faSearch,
    faArrowRightFromBracket,
    faWallet,
    faBars,
    faEllipsisVertical,
    faUsers,
    faBuildingColumns,
    faUser,
    faBuilding,
    faHouse,
    faGraduationCap,
    faPlane
} from '@fortawesome/free-solid-svg-icons';
import { useAppDispatch, useAppSelector } from '@/store/hooks';
import { logout } from '@/features/auth/store/authSlice';
import workspaceService from '../services/workspaceService';
import { Workspace } from '@/types/workspace';

const WorkspaceList: React.FC = () => {
    const navigate = useNavigate();
    const dispatch = useAppDispatch();
    const { user } = useAppSelector((state) => state.auth);
    const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeFilter, setActiveFilter] = useState('Todos');

    useEffect(() => {
        const fetchWorkspaces = async () => {
            try {
                setLoading(true);
                const data = await workspaceService.getWorkspaces();
                setWorkspaces(data);
                setError(null);
            } catch (err) {
                console.error('Failed to fetch workspaces:', err);
                setError('No se pudieron cargar los espacios de trabajo.');
            } finally {
                setLoading(false);
            }
        };

        fetchWorkspaces();
    }, []);

    const handleLogout = () => {
        dispatch(logout());
        navigate('/auth');
    };


    const getCategoryIcon = (category?: string) => {
        switch (category) {
            case 'Personal': return faUser;
            case 'Empresa': return faBuilding;
            case 'Hogar': return faHouse;
            case 'Inversión': return faChartLine;
            case 'Educación': return faGraduationCap;
            case 'Viajes': return faPlane;
            default: return faBuildingColumns;
        }
    };

    const allCategories = ['Personal', 'Empresa', 'Hogar', 'Inversión', 'Educación', 'Viajes'];
    const filterOptions = ['Todos', 'Míos', 'Compartidos', ...allCategories];

    const filteredWorkspaces = workspaces.filter(w => {
        if (activeFilter === 'Todos') return true;
        if (activeFilter === 'Míos') return w.role === 'owner';
        if (activeFilter === 'Compartidos') return w.role !== 'owner';
        return w.category === activeFilter;
    });

    return (
        <div className="flex h-screen w-full bg-background-light font-display overflow-hidden">
            {/* Sidebar Navigation */}
            <aside className="hidden md:flex flex-col w-72 h-full bg-[#111318] border-r border-slate-800 flex-shrink-0">
                <div className="p-6 pb-2">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center size-10 rounded-xl bg-primary/20 text-primary">
                            <FontAwesomeIcon icon={faWallet} className="text-2xl" />
                        </div>
                        <div className="flex flex-col">
                            <h1 className="text-white text-lg font-bold leading-none tracking-tight">WiseLab</h1>
                            <span className="text-slate-400 text-xs font-medium mt-1">Gestión Financiera</span>
                        </div>
                    </div>
                </div>

                <div className="flex-1 flex flex-col gap-2 px-4 py-6 overflow-y-auto">
                    <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Menú Principal</p>
                    <a className="flex items-center gap-3 px-4 py-3 rounded-lg bg-primary text-white shadow-lg shadow-primary/20" href="#">
                        <FontAwesomeIcon icon={faBuildingColumns} className="w-5" />
                        <span className="font-medium text-sm">Workspaces</span>
                    </a>
                </div>

                <div className="p-4 border-t border-slate-800">
                    <div className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors group">
                        <div className="flex items-center gap-3 truncate">
                            <div className="size-9 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                                {user?.name?.charAt(0) || user?.email.charAt(0).toUpperCase()}
                            </div>
                            <div className="flex flex-col truncate">
                                <p className="text-sm font-semibold text-white truncate">{user?.name || 'Usuario'}</p>
                                <p className="text-xs text-slate-400 truncate">{user?.email}</p>
                            </div>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="text-slate-400 hover:text-red-400 transition-colors p-2"
                            title="Cerrar Sesión"
                        >
                            <FontAwesomeIcon icon={faArrowRightFromBracket} />
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 h-full overflow-y-auto bg-background-light relative">
                {/* Decorative Background Icons */}
                <div className="absolute -right-20 -bottom-20 text-primary/[0.03] pointer-events-none transform -rotate-12 select-none z-0">
                    <FontAwesomeIcon icon={faChartLine} className="text-[400px]" />
                </div>

                {/* Mobile Header */}
                <div className="md:hidden flex items-center justify-between p-4 bg-[#111318] text-white sticky top-0 z-20">
                    <div className="flex items-center gap-2">
                        <FontAwesomeIcon icon={faWallet} className="text-primary text-xl" />
                        <span className="font-bold">WiseLab</span>
                    </div>
                    <button className="p-2">
                        <FontAwesomeIcon icon={faBars} />
                    </button>
                </div>

                {/* Page Content */}
                <div className="max-w-7xl mx-auto p-4 md:p-8 lg:p-12 relative z-10">
                    {/* Header Section */}
                    <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
                        <div className="flex flex-col gap-2">
                            <h2 className="text-3xl md:text-4xl font-black text-slate-900 tracking-tight">Tus Espacios de Trabajo</h2>
                            <p className="text-slate-500 text-base max-w-lg">
                                Gestiona tus presupuestos, rastrea gastos y colabora con tus equipos financieros en diferentes organizaciones.
                            </p>
                        </div>
                        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
                            <div className="relative group w-full md:w-64">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <FontAwesomeIcon icon={faSearch} className="text-slate-400 group-focus-within:text-primary" />
                                </div>
                                <input
                                    className="block w-full pl-10 pr-3 py-2.5 border-none rounded-xl bg-white text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary/50 sm:text-sm shadow-sm"
                                    placeholder="Buscar workspaces..."
                                    type="text"
                                />
                            </div>
                            <button
                                onClick={() => navigate('/work-in-progress')}
                                className="flex items-center justify-center gap-2 bg-primary hover:bg-blue-600 text-white px-5 py-2.5 rounded-xl font-bold shadow-lg shadow-primary/30 transition-all active:scale-95 whitespace-nowrap"
                            >
                                <FontAwesomeIcon icon={faPlus} />
                                <span>Nuevo Workspace</span>
                            </button>
                        </div>
                    </div>

                    {/* Filters */}
                    <div className="flex gap-2 mb-8 overflow-x-auto pb-2 scrollbar-hide">
                        {filterOptions.map(option => (
                            <button
                                key={option}
                                onClick={() => setActiveFilter(option)}
                                className={`px-4 py-1.5 rounded-full text-sm transition-all whitespace-nowrap ${activeFilter === option
                                    ? 'bg-primary text-white font-bold shadow-md'
                                    : 'bg-white border border-slate-200 text-slate-600 font-medium hover:border-primary hover:text-primary shadow-sm'
                                    }`}
                            >
                                {option}
                            </button>
                        ))}
                    </div>

                    {/* Grid Layout */}
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                        {loading ? (
                            // Loading Skeletons
                            [1, 2, 3].map(i => (
                                <div key={i} className="animate-pulse bg-white rounded-2xl border border-slate-200 p-6 h-[220px]">
                                    <div className="size-12 bg-slate-100 rounded-xl mb-4"></div>
                                    <div className="h-6 bg-slate-100 rounded mb-2 w-3/4"></div>
                                    <div className="h-4 bg-slate-100 rounded mb-6 w-full"></div>
                                </div>
                            ))
                        ) : error ? (
                            <div className="col-span-full p-8 bg-white rounded-2xl border border-red-100 text-center">
                                <p className="text-red-500 mb-4">{error}</p>
                                <button
                                    onClick={() => window.location.reload()}
                                    className="text-primary font-bold hover:underline"
                                >
                                    Reintentar
                                </button>
                            </div>
                        ) : (
                            <>
                                {filteredWorkspaces.map((workspace) => (
                                    <div
                                        key={workspace.id}
                                        onClick={() => navigate('/work-in-progress')}
                                        className="group relative flex flex-col bg-white rounded-2xl border border-slate-200 p-6 hover:border-primary/50 hover:shadow-xl hover:shadow-primary/5 transition-all duration-300 cursor-pointer text-left"
                                    >
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="flex items-center gap-3">
                                                <div className="p-3 rounded-xl bg-primary/10 text-primary">
                                                    <FontAwesomeIcon icon={getCategoryIcon(workspace.category)} className="text-xl" />
                                                </div>
                                                <div className="flex flex-col">
                                                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">Categoría</span>
                                                    <span className="text-sm font-bold text-slate-700 leading-none">{workspace.category || 'General'}</span>
                                                </div>
                                            </div>
                                            <button className="text-slate-400 hover:text-slate-600 transition-colors p-1">
                                                <FontAwesomeIcon icon={faEllipsisVertical} />
                                            </button>
                                        </div>
                                        <h3 className="text-xl font-bold text-slate-900 mb-2 group-hover:text-primary transition-colors truncate">
                                            {workspace.name}
                                        </h3>
                                        <p className="text-slate-500 text-sm mb-6 line-clamp-2">
                                            {workspace.description || 'Sin descripción disponible para este espacio.'}
                                        </p>
                                        <div className="mt-auto flex items-center justify-end border-t border-slate-100 pt-4">
                                            <div className="flex items-center gap-1.5 text-slate-500 text-sm">
                                                <FontAwesomeIcon icon={faUsers} className="text-xs" />
                                                <span>{workspace.members_count} Miembros</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}

                                {/* Create New Placeholder */}
                                <div
                                    onClick={() => navigate('/work-in-progress')}
                                    className="group relative flex flex-col items-center justify-center bg-transparent border-2 border-dashed border-slate-300 rounded-2xl p-6 hover:border-primary hover:bg-primary/5 transition-all duration-300 cursor-pointer min-h-[220px]"
                                >
                                    <div className="p-4 rounded-full bg-white shadow-sm border border-slate-200 group-hover:border-primary/50 mb-4 transition-colors">
                                        <FontAwesomeIcon icon={faPlus} className="text-3xl text-slate-400 group-hover:text-primary transition-colors" />
                                    </div>
                                    <h3 className="text-lg font-bold text-slate-900 mb-1">Crear Workspace</h3>
                                    <p className="text-slate-500 text-sm text-center">Empieza a gestionar un nuevo presupuesto</p>
                                </div>
                            </>
                        )}
                    </div>

                    {/* Pagination */}
                    {!loading && !error && filteredWorkspaces.length > 0 && (
                        <div className="flex items-center justify-between mt-10 pt-6 border-t border-slate-200">
                            <p className="text-sm text-slate-500">
                                Mostrando <span className="font-bold text-slate-900">{filteredWorkspaces.length}</span> de <span className="font-bold text-slate-900">{filteredWorkspaces.length}</span> espacios
                            </p>
                            <div className="flex gap-2">
                                <button className="px-4 py-2 text-sm font-bold rounded-xl border border-slate-200 text-slate-400 bg-slate-50 cursor-not-allowed" disabled>Atrás</button>
                                <button className="px-4 py-2 text-sm font-bold rounded-xl border border-slate-200 text-slate-400 bg-slate-50 cursor-not-allowed" disabled>Siguiente</button>
                            </div>
                        </div>
                    )}
                </div>

                {/* Floating Add Button Mobile */}
                <button
                    onClick={() => navigate('/work-in-progress')}
                    className="md:hidden fixed bottom-6 right-6 size-14 bg-primary text-white rounded-full shadow-xl hover:bg-blue-600 transition-colors z-50 flex items-center justify-center text-xl active:scale-95"
                >
                    <FontAwesomeIcon icon={faPlus} />
                </button>
            </main>
        </div>
    );
};

export default WorkspaceList;
