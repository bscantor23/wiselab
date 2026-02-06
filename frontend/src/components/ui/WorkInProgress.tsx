import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHammer, faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import Button from './Button';

const WorkInProgress: React.FC = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-background-light flex items-center justify-center p-6">
            <div className="text-center max-w-md">
                <div className="size-20 bg-primary/10 text-primary rounded-2xl flex items-center justify-center mx-auto mb-8 animate-bounce">
                    <FontAwesomeIcon icon={faHammer} className="text-4xl" />
                </div>

                <h1 className="text-3xl font-bold text-slate-900 mb-4">
                    Página en Construcción
                </h1>

                <p className="text-slate-600 mb-8 leading-relaxed">
                    Estamos trabajando duro para traerte esta funcionalidad. Pásate de nuevo pronto para ver las novedades de WiseLab.
                </p>

                <Button
                    variant="outline"
                    onClick={() => navigate('/workspaces')}
                    className="flex items-center gap-2 mx-auto"
                >
                    <FontAwesomeIcon icon={faArrowLeft} />
                    <span>Volver a Workspaces</span>
                </Button>
            </div>
        </div>
    );
};

export default WorkInProgress;
