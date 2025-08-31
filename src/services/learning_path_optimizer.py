"""
Learning Path Optimizer - Intelligently designs optimal learning sequences
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json

class LearningStyle(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

@dataclass
class SkillNode:
    """Represents a skill or topic with its dependencies and relationships"""
    id: str
    name: str
    difficulty: DifficultyLevel
    prerequisites: List[str]
    estimated_time: int  # minutes
    importance_score: float  # 0-1
    learning_style_preference: List[LearningStyle]
    related_skills: List[str]
    career_relevance: List[str]

@dataclass
class LearningPath:
    """Represents an optimized learning sequence"""
    user_id: str
    current_skills: List[str]
    target_skills: List[str]
    path_sequence: List[SkillNode]
    estimated_duration: int  # minutes
    confidence_score: float  # 0-1
    alternative_paths: List[List[SkillNode]]
    milestones: List[Dict]

class LearningPathOptimizer:
    def __init__(self):
        # Initialize skill dependency graph
        self.skill_graph = self._build_skill_graph()
        
    def _build_skill_graph(self) -> Dict[str, SkillNode]:
        """
        Build comprehensive skill dependency graph
        """
        return {
            "current_affairs_basics": SkillNode(
                id="current_affairs_basics",
                name="Current Affairs Basics",
                difficulty=DifficultyLevel.BEGINNER,
                prerequisites=[],
                estimated_time=30,
                importance_score=0.9,
                learning_style_preference=[LearningStyle.READING_WRITING, LearningStyle.AUDITORY],
                related_skills=["geography_basics", "history_basics"],
                career_relevance=["general_knowledge", "competitive_exams", "interviews"]
            ),
            "geography_basics": SkillNode(
                id="geography_basics",
                name="Geography Basics",
                difficulty=DifficultyLevel.BEGINNER,
                prerequisites=[],
                estimated_time=45,
                importance_score=0.8,
                learning_style_preference=[LearningStyle.VISUAL, LearningStyle.READING_WRITING],
                related_skills=["current_affairs_basics", "history_basics"],
                career_relevance=["competitive_exams", "tourism", "environmental_science"]
            ),
            "history_basics": SkillNode(
                id="history_basics",
                name="History Basics",
                difficulty=DifficultyLevel.BEGINNER,
                prerequisites=[],
                estimated_time=60,
                importance_score=0.7,
                learning_style_preference=[LearningStyle.READING_WRITING, LearningStyle.AUDITORY],
                related_skills=["current_affairs_basics", "geography_basics"],
                career_relevance=["competitive_exams", "education", "research"]
            ),
            "current_affairs_intermediate": SkillNode(
                id="current_affairs_intermediate",
                name="Current Affairs Intermediate",
                difficulty=DifficultyLevel.INTERMEDIATE,
                prerequisites=["current_affairs_basics", "geography_basics"],
                estimated_time=45,
                importance_score=0.85,
                learning_style_preference=[LearningStyle.READING_WRITING, LearningStyle.AUDITORY],
                related_skills=["economics_basics", "politics_basics"],
                career_relevance=["competitive_exams", "journalism", "public_policy"]
            ),
            "economics_basics": SkillNode(
                id="economics_basics",
                name="Economics Basics",
                difficulty=DifficultyLevel.INTERMEDIATE,
                prerequisites=["current_affairs_basics"],
                estimated_time=90,
                importance_score=0.8,
                learning_style_preference=[LearningStyle.READING_WRITING, LearningStyle.VISUAL],
                related_skills=["current_affairs_intermediate", "business_basics"],
                career_relevance=["competitive_exams", "finance", "business", "public_policy"]
            ),
            "science_tech_basics": SkillNode(
                id="science_tech_basics",
                name="Science & Technology Basics",
                difficulty=DifficultyLevel.BEGINNER,
                prerequisites=[],
                estimated_time=75,
                importance_score=0.75,
                learning_style_preference=[LearningStyle.VISUAL, LearningStyle.KINESTHETIC],
                related_skills=["current_affairs_basics"],
                career_relevance=["competitive_exams", "engineering", "research", "technology"]
            ),
            "science_tech_advanced": SkillNode(
                id="science_tech_advanced",
                name="Science & Technology Advanced",
                difficulty=DifficultyLevel.ADVANCED,
                prerequisites=["science_tech_basics", "current_affairs_intermediate"],
                estimated_time=120,
                importance_score=0.7,
                learning_style_preference=[LearningStyle.VISUAL, LearningStyle.KINESTHETIC],
                related_skills=["research_methods", "critical_thinking"],
                career_relevance=["research", "academia", "technology_leadership"]
            )
        }
    
    def optimize_learning_path(
        self, 
        user_id: str,
        current_skills: List[str],
        target_skills: List[str],
        user_preferences: Dict,
        time_constraints: Dict
    ) -> LearningPath:
        """
        Design optimal learning path for user
        """
        try:
            print(f"🎯 Optimizing learning path for user: {user_id}")
            print(f"Current skills: {current_skills}")
            print(f"Target skills: {target_skills}")
            
            # Step 1: Analyze skill gaps
            skill_gaps = self._analyze_skill_gaps(current_skills, target_skills)
            print(f"🔍 Identified skill gaps: {skill_gaps}")
            
            # Step 2: Build dependency tree
            dependency_tree = self._build_dependency_tree(skill_gaps)
            print(f"🌳 Built dependency tree with {len(dependency_tree)} nodes")
            
            # Step 3: Optimize learning sequence
            optimal_sequence = self._optimize_sequence(
                dependency_tree, 
                user_preferences, 
                time_constraints
            )
            print(f"📚 Optimized sequence: {[node.name for node in optimal_sequence]}")
            
            # Step 4: Generate alternative paths
            alternative_paths = self._generate_alternative_paths(
                dependency_tree, 
                optimal_sequence, 
                user_preferences
            )
            
            # Step 5: Create milestones
            milestones = self._create_milestones(optimal_sequence)
            
            # Step 6: Calculate confidence and duration
            confidence_score = self._calculate_confidence(optimal_sequence, skill_gaps)
            estimated_duration = sum(node.estimated_time for node in optimal_sequence)
            
            return LearningPath(
                user_id=user_id,
                current_skills=current_skills,
                target_skills=target_skills,
                path_sequence=optimal_sequence,
                estimated_duration=estimated_duration,
                confidence_score=confidence_score,
                alternative_paths=alternative_paths,
                milestones=milestones
            )
            
        except Exception as e:
            print(f"❌ Error optimizing learning path: {e}")
            raise
    
    def _analyze_skill_gaps(self, current_skills: List[str], target_skills: List[str]) -> List[str]:
        """
        Identify skills user needs to learn to reach targets
        """
        gaps = []
        
        for target in target_skills:
            if target not in current_skills:
                # Add target skill
                if target in self.skill_graph:
                    gaps.append(target)
                
                # Add prerequisites
                if target in self.skill_graph:
                    for prereq in self.skill_graph[target].prerequisites:
                        if prereq not in current_skills and prereq not in gaps:
                            gaps.append(prereq)
        
        return gaps
    
    def _build_dependency_tree(self, skill_gaps: List[str]) -> List[SkillNode]:
        """
        Build dependency tree for skills to be learned
        """
        tree = []
        processed = set()
        
        def add_with_dependencies(skill_id: str):
            if skill_id in processed or skill_id not in self.skill_graph:
                return
            
            # Add prerequisites first
            for prereq in self.skill_graph[skill_id].prerequisites:
                if prereq not in processed:
                    add_with_dependencies(prereq)
            
            # Add current skill
            tree.append(self.skill_graph[skill_id])
            processed.add(skill_id)
        
        # Process all skill gaps
        for skill in skill_gaps:
            add_with_dependencies(skill)
        
        return tree
    
    def _optimize_sequence(
        self, 
        dependency_tree: List[SkillNode], 
        user_preferences: Dict, 
        time_constraints: Dict
    ) -> List[SkillNode]:
        """
        Optimize learning sequence based on user preferences and constraints
        """
        if not dependency_tree:
            return []
        
        # Sort by importance, difficulty, and user preferences
        def sort_key(node: SkillNode) -> Tuple[float, int, float]:
            # Higher importance = higher priority
            importance = node.importance_score
            
            # Lower difficulty = higher priority (easier first)
            difficulty_priority = {
                DifficultyLevel.BEGINNER: 3,
                DifficultyLevel.INTERMEDIATE: 2,
                DifficultyLevel.ADVANCED: 1
            }
            difficulty = difficulty_priority[node.difficulty]
            
            # Learning style preference match
            style_match = 0
            if 'learning_style' in user_preferences:
                user_style = user_preferences['learning_style']
                if user_style in node.learning_style_preference:
                    style_match = 1
            
            return (importance, difficulty, style_match)
        
        # Sort and return optimized sequence
        optimized = sorted(dependency_tree, key=sort_key, reverse=True)
        return optimized
    
    def _generate_alternative_paths(
        self, 
        dependency_tree: List[SkillNode], 
        primary_path: List[SkillNode], 
        user_preferences: Dict
    ) -> List[List[SkillNode]]:
        """
        Generate alternative learning paths for flexibility
        """
        alternatives = []
        
        if len(dependency_tree) <= 1:
            return alternatives
        
        # Alternative 1: Focus on user's preferred learning style
        if 'learning_style' in user_preferences:
            preferred_style = user_preferences['learning_style']
            style_focused = [node for node in dependency_tree 
                           if preferred_style in node.learning_style_preference]
            if style_focused and style_focused != primary_path:
                alternatives.append(style_focused)
        
        # Alternative 2: Quick path (focus on high-importance, low-time skills)
        quick_path = sorted(dependency_tree, 
                           key=lambda x: x.importance_score / x.estimated_time, 
                           reverse=True)
        if quick_path != primary_path:
            alternatives.append(quick_path[:len(primary_path)//2])  # Shorter path
        
        # Alternative 3: Comprehensive path (include all related skills)
        comprehensive = []
        for node in primary_path:
            comprehensive.append(node)
            # Add related skills
            for related_id in node.related_skills:
                if related_id in self.skill_graph and related_id not in [n.id for n in comprehensive]:
                    comprehensive.append(self.skill_graph[related_id])
        
        if comprehensive != primary_path:
            alternatives.append(comprehensive)
        
        return alternatives
    
    def _create_milestones(self, sequence: List[SkillNode]) -> List[Dict]:
        """
        Create learning milestones for motivation and tracking
        """
        milestones = []
        
        for i, node in enumerate(sequence):
            milestone = {
                "id": f"milestone_{i+1}",
                "name": f"Master {node.name}",
                "skill_id": node.id,
                "position": i + 1,
                "estimated_time": node.estimated_time,
                "difficulty": node.difficulty.value,
                "description": f"Complete {node.name} to unlock next learning opportunities",
                "reward": f"Access to {len(node.related_skills)} related skills"
            }
            milestones.append(milestone)
        
        return milestones
    
    def _calculate_confidence(self, sequence: List[SkillNode], skill_gaps: List[str]) -> float:
        """
        Calculate confidence score for the learning path
        """
        if not sequence:
            return 0.0
        
        # Factors affecting confidence:
        # 1. Coverage of skill gaps
        coverage = len([skill for skill in skill_gaps if skill in [node.id for node in sequence]])
        coverage_score = coverage / len(skill_gaps) if skill_gaps else 1.0
        
        # 2. Prerequisite satisfaction
        prereq_satisfaction = 1.0
        for node in sequence:
            for prereq in node.prerequisites:
                if prereq not in [n.id for n in sequence[:sequence.index(node)]]:
                    prereq_satisfaction *= 0.8  # Reduce confidence for missing prereqs
        
        # 3. Difficulty progression
        difficulty_progression = 1.0
        difficulties = [node.difficulty.value for node in sequence]
        for i in range(1, len(difficulties)):
            if difficulties[i] < difficulties[i-1]:  # Harder before easier
                difficulty_progression *= 0.9
        
        # Calculate final confidence
        confidence = (coverage_score * 0.4 + prereq_satisfaction * 0.4 + difficulty_progression * 0.2)
        return min(confidence, 1.0)
    
    def get_next_learning_recommendation(
        self, 
        user_id: str, 
        current_progress: Dict,
        user_preferences: Dict = None
    ) -> Dict:
        """
        Get immediate next learning recommendation for user
        """
        try:
            # Extract current skills from progress
            current_skills = list(current_progress.get("topic_performance", {}).keys())
            
            # Determine target skills based on user preferences
            if not user_preferences:
                user_preferences = {"learning_style": "reading_writing"}
            
            # Get all available skills from vector database (more accurate)
            all_skills_data = self.get_all_available_skills()
            all_skills = [skill["id"] for skill in all_skills_data]
            
            # Find next logical skill to learn
            next_skill = self._find_next_skill_from_vector_db(current_skills, all_skills_data, user_preferences)
            
            if next_skill:
                return {
                    "next_skill": {
                        "id": next_skill["id"],
                        "name": next_skill["name"],
                        "difficulty": next_skill["difficulty"],
                        "estimated_time": next_skill["estimated_time"],
                        "why_important": f"Builds on your knowledge of {', '.join(next_skill['prerequisites']) if next_skill['prerequisites'] else 'general knowledge'}",
                        "learning_tips": self._get_learning_tips_from_vector_db(next_skill, user_preferences)
                    },
                    "learning_path": {
                        "current_position": len(current_skills),
                        "total_skills": len(all_skills),
                        "progress_percentage": (len(current_skills) / len(all_skills)) * 100
                    }
                }
            else:
                return {
                    "message": "Congratulations! You've mastered all available skills.",
                    "suggestion": "Consider exploring advanced topics or related subjects."
                }
                
        except Exception as e:
            print(f"❌ Error getting next recommendation: {e}")
            return {"error": "Unable to generate recommendation"}
    
    def _find_next_skill_from_vector_db(
        self, 
        current_skills: List[str], 
        all_skills_data: List[Dict], 
        user_preferences: Dict
    ) -> Optional[Dict]:
        """
        Find the next logical skill to learn from vector database data
        """
        available_skills = [skill for skill in all_skills_data if skill["id"] not in current_skills]
        
        if not available_skills:
            return None
        
        # Score each available skill
        skill_scores = {}
        for skill in available_skills:
            # Check if prerequisites are met
            prereqs_met = all(prereq in current_skills for prereq in skill.get("prerequisites", []))
            if not prereqs_met:
                continue
            
            # Calculate score based on multiple factors
            score = 0
            
            # 1. Importance score
            score += skill.get("importance_score", 0.5) * 0.4
            
            # 2. Learning style match (if available)
            if 'learning_style' in user_preferences:
                user_style = user_preferences['learning_style']
                if user_style in skill.get("labels", []):
                    score += 0.3
            
            # 3. Related to current skills
            related_skills = skill.get("related_skills", [])
            if related_skills:
                related_count = len([s for s in related_skills if s in current_skills])
                score += (related_count / len(related_skills)) * 0.2
            
            # 4. Difficulty progression (prefer easier skills)
            difficulty = skill.get("difficulty", "Medium")
            if difficulty == "Easy":
                score += 0.1
            elif difficulty == "Medium":
                score += 0.05
            
            skill_scores[skill["id"]] = score
        
        if not skill_scores:
            return None
        
        # Return skill with highest score
        best_skill_id = max(skill_scores, key=skill_scores.get)
        return next(skill for skill in all_skills_data if skill["id"] == best_skill_id)
    
    def _get_learning_tips_from_vector_db(self, skill_data: Dict, user_preferences: Dict) -> List[str]:
        """
        Generate personalized learning tips from vector database skill data
        """
        tips = []
        
        # General tips based on difficulty
        difficulty = skill_data.get("difficulty", "Medium")
        if difficulty == "Easy":
            tips.append("Start with basic concepts and build gradually")
            tips.append("Use visual aids and real-world examples")
        elif difficulty == "Medium":
            tips.append("Connect new concepts to what you already know")
            tips.append("Practice with varied examples")
        else:  # Hard
            tips.append("Focus on deep understanding rather than memorization")
            tips.append("Apply concepts to complex scenarios")
        
        # Style-specific tips based on labels
        if 'learning_style' in user_preferences:
            style = user_preferences['learning_style']
            if style == "visual":
                tips.append("Use diagrams, charts, and mind maps")
            elif style == "auditory":
                tips.append("Read aloud and discuss with others")
            elif style == "kinesthetic":
                tips.append("Practice with hands-on activities")
            elif style == "reading_writing":
                tips.append("Take detailed notes and summarize key points")
        
        # Topic-specific tips based on labels
        labels = skill_data.get("labels", [])
        if "competitive_exams" in labels:
            tips.append("Focus on key concepts frequently tested in exams")
        if "interview_prep" in labels:
            tips.append("Practice explaining concepts in simple terms")
        if "general_knowledge" in labels:
            tips.append("Connect to current events and real-world applications")
        
        # Time management tips
        estimated_time = skill_data.get("estimated_time", 60)
        if estimated_time > 60:
            tips.append("Break this into smaller 30-minute sessions")
        
        return tips

    def get_all_available_skills(self) -> List[Dict]:
        """
        Get all available skills in the system - now from vector database for accuracy
        """
        try:
            # Try to get skills from vector database first (more accurate)
            from src.vector_store.qdrant_utils import get_all_available_skills_from_vector_db
            vector_skills = get_all_available_skills_from_vector_db()
            
            if vector_skills:
                print(f"🎯 Using {len(vector_skills)} skills from vector database")
                return vector_skills
            else:
                print("⚠️ No skills found in vector DB, falling back to hardcoded skills")
                
        except Exception as e:
            print(f"❌ Error fetching from vector DB: {e}, falling back to hardcoded skills")
        
        # Fallback to hardcoded skills if vector DB fails
        skills = []
        for skill_id, skill_node in self.skill_graph.items():
            skills.append({
                "id": skill_id,
                "name": skill_node.name,
                "difficulty": skill_node.difficulty.value,
                "estimated_time": skill_node.estimated_time,
                "importance_score": skill_node.importance_score,
                "prerequisites": skill_node.prerequisites,
                "related_skills": skill_node.related_skills,
                "career_relevance": skill_node.career_relevance,
                "labels": self._get_hardcoded_labels(skill_node),
                "available_difficulties": [skill_node.difficulty.value],
                "question_count": 0  # Unknown for hardcoded skills
            })
        
        # Sort by importance and difficulty
        skills.sort(key=lambda x: (x["importance_score"], x["difficulty"]), reverse=True)
        return skills
    
    def _get_hardcoded_labels(self, skill_node: SkillNode) -> List[str]:
        """Generate labels for hardcoded skills"""
        labels = []
        
        # Add difficulty-based labels
        if skill_node.difficulty == DifficultyLevel.BEGINNER:
            labels.append('foundation')
        elif skill_node.difficulty == DifficultyLevel.INTERMEDIATE:
            labels.append('intermediate')
        elif skill_node.difficulty == DifficultyLevel.ADVANCED:
            labels.append('specialized')
        
        # Add learning style labels
        for style in skill_node.learning_style_preference:
            labels.append(style.value)
        
        # Add career relevance labels
        labels.extend(skill_node.career_relevance)
        
        # Add general labels
        labels.extend(['competitive_exams', 'general_knowledge'])
        
        return list(set(labels))  # Remove duplicates

# Global instance
learning_path_optimizer = LearningPathOptimizer() 