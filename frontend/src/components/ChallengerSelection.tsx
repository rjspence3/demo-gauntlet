import React, { useState } from 'react';

export interface Challenger {
    id: string;
    name: string;
    role: string;
    description: string;
    tags: string[];
    evidenceCount: number; // For the progress bar
}

interface ChallengerSelectionProps {
    challengers: Challenger[];
    onStartSimulation: (selectedIds: string[]) => void;
}

export const ChallengerSelection: React.FC<ChallengerSelectionProps> = ({
    challengers,
    onStartSimulation
}) => {
    // Default to selecting the first 3 (usually strongest)
    const [selectedIds, setSelectedIds] = useState<string[]>(
        challengers.slice(0, 3).map(c => c.id)
    );

    const toggleChallenger = (id: string) => {
        setSelectedIds(prev =>
            prev.includes(id)
                ? prev.filter(cId => cId !== id)
                : [...prev, id]
        );
    };

    const currentCount = selectedIds.length;
    // Recommend 2-4 challengers
    const isCountOptimal = currentCount >= 2 && currentCount <= 4;

    return (
        <div className="max-w-5xl mx-auto p-6 min-h-[600px] flex flex-col">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Choose Your Challengers</h1>
                <p className="text-gray-600 mt-2">
                    Select who will be in the room. We recommend 2-4 challengers based on your deck's content.
                </p>
            </div>

            <div className="flex-1">
                <div className="grid grid-cols-1 gap-4">
                    <div className="grid grid-cols-12 gap-4 px-4 py-2 text-sm font-medium text-gray-500 border-b border-gray-200">
                        <div className="col-span-5">Identity</div>
                        <div className="col-span-5">Contextual Evidence</div>
                        <div className="col-span-2 text-right">Action</div>
                    </div>

                    {challengers.map((challenger) => {
                        const isSelected = selectedIds.includes(challenger.id);
                        const evidencePercent = Math.min(100, (challenger.evidenceCount / 10) * 100); // normalized to 10 for demo

                        return (
                            <div
                                key={challenger.id}
                                className={`
                  grid grid-cols-12 gap-4 items-center p-4 rounded-xl border transition-all duration-200
                  ${isSelected
                                        ? 'bg-white border-blue-200 shadow-sm'
                                        : 'bg-gray-50 border-transparent opacity-80 hover:opacity-100'
                                    }
                `}
                            >
                                {/* Identity */}
                                <div className="col-span-5">
                                    <div className="flex items-center">
                                        <div className={`
                      w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold mr-3
                      ${isSelected ? 'bg-blue-100 text-blue-700' : 'bg-gray-200 text-gray-500'}
                    `}>
                                            {challenger.name.charAt(0)}
                                        </div>
                                        <div>
                                            <h3 className={`font-semibold ${isSelected ? 'text-gray-900' : 'text-gray-600'}`}>
                                                {challenger.name}
                                            </h3>
                                            <p className="text-sm text-gray-500">{challenger.role}</p>
                                        </div>
                                    </div>
                                </div>

                                {/* Evidence Bar */}
                                <div className="col-span-5">
                                    <div className="flex items-center space-x-3">
                                        <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full ${isSelected ? 'bg-blue-500' : 'bg-gray-400'}`}
                                                style={{ width: `${evidencePercent}%` }}
                                            />
                                        </div>
                                        <span className="text-xs text-gray-500 font-medium w-16 text-right">
                                            {challenger.evidenceCount} facts
                                        </span>
                                    </div>
                                    <div className="flex flex-wrap gap-1 mt-1.5">
                                        {challenger.tags.slice(0, 3).map(tag => (
                                            <span key={tag} className="text-[10px] px-1.5 py-0.5 bg-gray-100 text-gray-600 rounded">
                                                #{tag}
                                            </span>
                                        ))}
                                    </div>
                                </div>

                                {/* Action */}
                                <div className="col-span-2 flex justify-end">
                                    <button
                                        onClick={() => toggleChallenger(challenger.id)}
                                        className={`
                      px-4 py-1.5 rounded-lg text-sm font-medium transition-colors
                      ${isSelected
                                                ? 'bg-blue-50 text-blue-700 hover:bg-blue-100 border border-blue-200'
                                                : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
                                            }
                    `}
                                    >
                                        {isSelected ? 'Selected' : 'Select'}
                                    </button>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-100 flex justify-between items-center">
                <div className="text-sm text-gray-500">
                    {selectedIds.length} challengers selected
                    {!isCountOptimal && (
                        <span className="text-amber-600 ml-2 font-medium">
                            (We recommend 2-4)
                        </span>
                    )}
                </div>
                <button
                    onClick={() => onStartSimulation(selectedIds)}
                    disabled={selectedIds.length === 0}
                    className={`
            px-8 py-3 rounded-xl font-bold text-white shadow-md transition-all
            ${selectedIds.length === 0
                            ? 'bg-gray-300 cursor-not-allowed'
                            : 'bg-gray-900 hover:bg-black hover:scale-105 active:scale-95'
                        }
          `}
                >
                    Enter Demo Room →
                </button>
            </div>
        </div>
    );
};
