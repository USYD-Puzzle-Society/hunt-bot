SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP TABLE IF EXISTS public.teams CASCADE;
DROP TABLE IF EXISTS public.players CASCADE;
DROP TABLE IF EXISTS public.puzzles CASCADE;
DROP TABLE IF EXISTS public.submissions CASCADE;

CREATE TABLE public.teams (
    team_name text PRIMARY KEY,
    category_channel_id text NOT NULL,
    voice_channel_id text NOT NULL,
    text_channel_id text NOT NULL,
    team_role_id text NOT NULL,
    puzzle_solved integer NOT NULL default 0
);

CREATE TABLE public.players (
    discord_id text PRIMARY KEY,
    team_name text NOT NULL REFERENCES public.teams ON DELETE CASCADE
);

CREATE TABLE public.puzzles (
    puzzle_id text PRIMARY KEY,
    puzzle_name text NOT NULL,
    puzzle_answer text NOT NULL,
    puzzle_author text NOT NULL,
    puzzle_link text NOT NULL,
    uni text NOT NULL
);

CREATE TABLE public.submissions (
    puzzle_id text NOT NULL REFERENCES public.puzzles ON DELETE CASCADE,    
    team_name text NOT NULL REFERENCES public.teams ON DELETE CASCADE,
    submission_time timestamptz NOT NULL,
    submission_answer text NOT NULL,
    submission_is_correct boolean NOT NULL
);
