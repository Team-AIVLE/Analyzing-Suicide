(Section 4) 선형사상

(subsection 4.1) Linear map

(정의 4.1.1) V,W 가 F-위의 벡터공간일 때, 함수 \(L : V \to W\) 가 다음 조건을 만족하면 L을 linear map (선형사상, linear mapping, linear transformation from V into W) 라고 부른다.

\(L(v_{1} + v_{2}) = L(v_{1}) + L(v_{2}) (v_{1}, v_{2} \in V)\)

\(L(av) = aL(v) ( v \in V , a \in F)\)

(관찰 4.1.2) \(L : V \to W\) 가 linear map 일 때,

\( L(0) = 0\)

\(v \in V\) 이면, \(L(-v) = -L(v)\)

\(u,v \in V\) 이면, \(L(u-v) = L(u) – L(v)\)

(정의 4.1.3) \(L : V \to W\) 가 linear map일 때,

L 이 injective (단사) 이면, L을 monomorphism 이라 부른다.

L 이 surjective (전사) 이면, L 을 epimorphism 이라고 부른다.

L 이 bijective (전단사) 이면, L을 isomorphism 이라고 부른다.

V = W 이면, L 을 endomorphism, 혹은 Linear operator, 혹은 간단히 operator 라 부른다.

Bijective endomorphism 은 automorphism 이라고 부른다.

(관찰 4.1.4) \(L : V \to W\) 가 linear map 일 때, 다음 조건은 동치이다.

L 은 isomorphism.

[\(M \bullet L = I_{V}\) 이고\( L \bullet M = I_{W}\) ] 인 linear map\(M : W \to V\) 가 존재.

(정의 4.1.5)\( L : V \to W\) 가 linear map 일 때,

\(ker L = L^{-1} (0) = {v \in V | L(v) = 0}\) 을 L 의 kernel 이라고 부른다.

\(im L = L(V) = {L(v) | v \in V}\) 를 L의 image 라고 부른다.

(관찰 4.1.6) \(L : V \to W\) 가 linear map 이면, \(ker L \le V , im L \le W\) 이다.

(관찰 4.1.8) \(L : V \to W\) 가 linear map 일 때, 다음 조건은 동치이다.

L 은 monomorphism 이다.

\(u,v, \in V\) 이고 \(Lu = Lv\) 이면, \(u = v \)이다.

\(v \in V\) 이고\(Lv = L0\) 이면, \(v = 0\) 이다.

\(ker L = 0\) 이다.